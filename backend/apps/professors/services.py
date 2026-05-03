"""
Service layer for the professors module.

Covers:
    - Professor profile CRUD (create for existing user, update, get, delete)
    - Combined User + ProfessorProfile creation
    - Admin dashboard aggregations
    - Professor dashboard aggregations
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Union

from django.db import transaction
from django.db.models import Count, Max, Q
from django.utils import timezone

from apps.accounts.models import ProfessorProfile, User
from apps.courses.models import Course, CourseStatus, CourseTest, TestQuestion
from apps.enrollments.models import Enrollment
from apps.permissions.models import Role


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _get_role(name: str) -> Optional[Role]:
    return Role.objects.filter(name=name).first()


# --------------------------------------------------------------------------- #
# Profile CRUD
# --------------------------------------------------------------------------- #
def get_profile_by_user_id(user_id: int) -> Optional[ProfessorProfile]:
    return ProfessorProfile.objects.filter(user_id=user_id).first()


def add_profile_to_existing_user(
    user_id: int, payload: dict
) -> Union[ProfessorProfile, str]:
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return "UserNotFound"
    if ProfessorProfile.objects.filter(user_id=user_id).exists():
        return "ProfileAlreadyExists"
    return ProfessorProfile.objects.create(user=user, **payload)


def update_profile(
    user_id: int, payload: dict
) -> Optional[ProfessorProfile]:
    profile = get_profile_by_user_id(user_id)
    if not profile:
        return None
    for field, value in payload.items():
        setattr(profile, field, value)
    profile.save()
    return profile


def delete_profile(user_id: int) -> Optional[ProfessorProfile]:
    profile = get_profile_by_user_id(user_id)
    if not profile:
        return None
    profile.delete()
    return profile


# --------------------------------------------------------------------------- #
# Combined User + Profile creation
# --------------------------------------------------------------------------- #
USER_FIELDS = {"email", "name", "phone", "country", "birthdate"}
PROFILE_FIELDS = {
    "specialization", "bio", "education", "experience", "skills", "social_links"
}


@transaction.atomic
def create_professor_user_and_profile(payload: dict) -> Union[User, str]:
    if User.objects.filter(email=payload["email"]).exists():
        return "EmailAlreadyExists"

    professor_role = _get_role("professor")
    if not professor_role:
        return "ProfessorRoleMissing"

    user_data = {k: v for k, v in payload.items() if k in USER_FIELDS}
    profile_data = {k: v for k, v in payload.items() if k in PROFILE_FIELDS}

    user = User(role=professor_role, **user_data)
    user.set_password(payload["password"])
    user.save()

    ProfessorProfile.objects.create(user=user, **profile_data)
    return user


# --------------------------------------------------------------------------- #
# Admin dashboard
# --------------------------------------------------------------------------- #
def get_admin_dashboard_stats() -> dict:
    professor_role = _get_role("professor")
    total_professors = (
        User.objects.filter(role=professor_role).count() if professor_role else 0
    )
    one_month_ago = timezone.now() - timedelta(days=30)
    new_users_last_month = User.objects.filter(created_at__gte=one_month_ago).count()
    return {
        "total_users": User.objects.count(),
        "total_professors": total_professors,
        "total_courses": Course.objects.count(),
        # Note: FastAPI calls this "new_enrollments_last_month" but actually
        # counts new users in last 30 days. We keep parity.
        "new_enrollments_last_month": new_users_last_month,
    }


def get_admin_professors() -> List[dict]:
    professor_role = _get_role("professor")
    if not professor_role:
        return []

    out: List[dict] = []
    professors = User.objects.filter(role=professor_role).select_related(
        "professor_profile"
    )
    for prof in professors:
        prof_courses = Course.objects.filter(instructor_id=prof.id)
        published = prof_courses.filter(status=CourseStatus.PUBLISHED)
        latest = published.aggregate(d=Max("created_at"))["d"]

        students_count = (
            Enrollment.objects.filter(course__instructor_id=prof.id)
            .values("user_id")
            .distinct()
            .count()
        )
        active_students_count = (
            Enrollment.objects.filter(
                course__instructor_id=prof.id, user__is_active=True
            )
            .values("user_id")
            .distinct()
            .count()
        )

        specialization = None
        try:
            specialization = prof.professor_profile.specialization
        except ProfessorProfile.DoesNotExist:
            pass

        out.append({
            "id": prof.id,
            "name": prof.name or "N/A",
            "email": prof.email,
            "courses_count": prof_courses.count(),
            "published_courses_count": published.count(),
            "students_count": students_count,
            "active_students_count": active_students_count,
            "average_rating": 0.0,
            "specialization": specialization,
            "phone": prof.phone,
            "is_active": bool(prof.is_active),
            "latest_course_published_at": (
                latest.isoformat() + "Z" if latest else None
            ),
        })
    return out


def get_courses_for_professor_admin(
    professor_id: int, skip: int = 0, limit: int = 100
) -> List[Course]:
    return list(
        Course.objects.filter(instructor_id=professor_id)
        .order_by("-updated_at")[skip : skip + limit]
    )


def get_admin_recent_activities() -> List[dict]:
    activities: List[dict] = []

    for course in Course.objects.select_related("instructor").order_by("-created_at")[:3]:
        instructor_name = "Unknown Instructor"
        if course.instructor:
            instructor_name = course.instructor.name or course.instructor.email
        activities.append({
            "id": f"course-{course.id}",
            "user_name": instructor_name,
            "action": "created_course",
            "resource_name": course.title,
            "timestamp": course.created_at.isoformat() + "Z",
        })

    for user in User.objects.order_by("-created_at")[:3]:
        activities.append({
            "id": f"user-{user.id}",
            "user_name": user.name or user.email,
            "action": "Enregistrement d'un utilisateur ",
            "resource_name": user.email,
            "timestamp": user.created_at.isoformat() + "Z",
        })

    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:5]


def get_admin_user_distribution() -> dict:
    def _count_for(name: str) -> int:
        role = _get_role(name)
        return User.objects.filter(role=role).count() if role else 0

    admins_count = _count_for("admin") + _count_for("super_admin")
    return {
        "students_count": _count_for("student"),
        "professors_count": _count_for("professor"),
        "admins_count": admins_count,
    }


def get_admin_monthly_registrations() -> List[dict]:
    """Last 6 months of user registrations including current."""
    out: List[dict] = []
    today = timezone.now()
    for i in range(5, -1, -1):
        target = today - timedelta(days=i * 30)
        month_start = datetime(target.year, target.month, 1, tzinfo=today.tzinfo)
        if month_start.month == 12:
            next_month = datetime(month_start.year + 1, 1, 1, tzinfo=today.tzinfo)
        else:
            next_month = datetime(
                month_start.year, month_start.month + 1, 1, tzinfo=today.tzinfo
            )
        count = User.objects.filter(
            created_at__gte=month_start, created_at__lt=next_month
        ).count()
        out.append({"month": month_start.strftime("%b"), "count": count})
    return out


# --------------------------------------------------------------------------- #
# Professor dashboard
# --------------------------------------------------------------------------- #
def get_professor_dashboard_stats(user) -> dict:
    qs = Course.objects.filter(instructor_id=user.id)
    published = qs.filter(status=CourseStatus.PUBLISHED)

    total_students = (
        Enrollment.objects.filter(course__instructor_id=user.id)
        .values("user_id")
        .distinct()
        .count()
    )
    total_questions = TestQuestion.objects.filter(
        test__section__course__instructor_id=user.id
    ).count()
    return {
        "published_courses_count": published.count(),
        "total_students_count": total_students,
        "average_rating": 0.0,
        "total_questions_count": total_questions,
    }


def get_professor_published_courses(user) -> List[dict]:
    out: List[dict] = []
    courses = Course.objects.filter(
        instructor_id=user.id, status=CourseStatus.PUBLISHED
    )
    for course in courses:
        students_count = (
            Enrollment.objects.filter(course_id=course.id)
            .values("user_id")
            .distinct()
            .count()
        )
        last_updated = (
            course.updated_at.isoformat() + "Z"
            if course.updated_at
            else timezone.now().isoformat() + "Z"
        )
        out.append({
            "id": course.id,
            "title": course.title,
            "students_count": students_count,
            "rating": 0.0,
            "last_updated": last_updated,
        })
    return out


def get_professor_student_engagement(user) -> List[dict]:
    titles = Course.objects.filter(
        instructor_id=user.id, status=CourseStatus.PUBLISHED
    ).values_list("title", flat=True)
    return [
        {"course_name": title, "average_hours_spent": 0.0}
        for title in titles
    ]


def get_professor_student_distribution(user) -> dict:
    active_students_count = (
        Enrollment.objects.filter(course__instructor_id=user.id)
        .values("user_id")
        .distinct()
        .count()
    )
    return {
        "active_students_count": active_students_count,
        "inactive_students_count": 0,
        "completed_students_count": 0,
    }


def get_professor_recent_activities(user) -> List[dict]:
    """No activity log model exists yet — returns empty list (parity with FastAPI)."""
    return []
