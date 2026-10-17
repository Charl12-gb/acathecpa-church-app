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
from django.db.models import Avg, Count, Max, Q, Sum
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


def get_or_create_profile(user: User) -> ProfessorProfile:
    profile, _ = ProfessorProfile.objects.get_or_create(
        user=user, defaults={"specialization": ""}
    )
    return profile


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
def _instructor_enrollments(user):
    return Enrollment.objects.filter(course__instructor_id=user.id)


def get_professor_dashboard_stats(user) -> dict:
    from apps.enrollments.models import Certificate
    from apps.payments.models import Payment, PaymentStatus

    published = Course.objects.filter(instructor_id=user.id, status=CourseStatus.PUBLISHED)
    revenue = (
        Payment.objects.filter(course__instructor_id=user.id, status=PaymentStatus.COMPLETED)
        .aggregate(total=Sum("amount"))["total"]
    )
    return {
        "published_courses_count": published.count(),
        "total_students_count": _instructor_enrollments(user).values("user_id").distinct().count(),
        "certificates_count": Certificate.objects.filter(course__instructor_id=user.id).count(),
        "revenue": float(revenue or 0),
        "total_questions_count": TestQuestion.objects.filter(
            test__section__course__instructor_id=user.id
        ).count(),
    }


def get_professor_published_courses(user) -> List[dict]:
    courses = (
        Course.objects.filter(instructor_id=user.id, status=CourseStatus.PUBLISHED)
        .annotate(
            students=Count("enrollments", distinct=True),
            avg_progress=Avg("enrollments__progress_percentage"),
        )
    )
    return [
        {
            "id": course.id,
            "title": course.title,
            "students_count": course.students,
            "average_progress": round(course.avg_progress or 0, 1),
            "last_updated": (course.updated_at or timezone.now()).isoformat(),
        }
        for course in courses
    ]


def get_professor_student_engagement(user) -> List[dict]:
    """Average progress of the students of each published course."""
    courses = (
        Course.objects.filter(instructor_id=user.id, status=CourseStatus.PUBLISHED)
        .annotate(avg_progress=Avg("enrollments__progress_percentage"))
    )
    return [
        {"course_name": c.title, "average_progress": round(c.avg_progress or 0, 1)}
        for c in courses
    ]


def get_professor_student_distribution(user) -> dict:
    """
    Per enrollment: completed (certificate stage reached), active (started),
    inactive (enrolled but nothing done yet).
    """
    qs = _instructor_enrollments(user)
    completed = qs.filter(completed_at__isnull=False).count()
    inactive = qs.filter(completed_at__isnull=True, progress_percentage=0).count()
    return {
        "active_students_count": qs.count() - completed - inactive,
        "inactive_students_count": inactive,
        "completed_students_count": completed,
    }


def get_professor_recent_activities(user, limit: int = 8) -> List[dict]:
    """Latest enrollments, quiz attempts and certificates on the professor's courses."""
    from apps.enrollments.models import Certificate

    def _name(u):
        return u.name or u.email.split("@")[0]

    events: List[dict] = []
    for e in _instructor_enrollments(user).select_related("user", "course").order_by("-enrolled_at")[:limit]:
        events.append({
            "id": f"enroll-{e.id}", "student_name": _name(e.user), "course_name": e.course.title,
            "activity_type": "enrollment", "content": "S'est inscrit au cours",
            "timestamp": e.enrolled_at.isoformat(),
        })
        for i, a in enumerate(e.test_attempts or []):
            events.append({
                "id": f"quiz-{e.id}-{i}", "student_name": _name(e.user), "course_name": e.course.title,
                "activity_type": "quiz",
                "content": f"Quiz {'réussi' if a.get('passed') else 'échoué'} ({a.get('score', 0)} %)",
                "timestamp": a.get("attempted_at") or e.enrolled_at.isoformat(),
            })
    for c in Certificate.objects.filter(course__instructor_id=user.id).select_related("user", "course").order_by("-issue_date")[:limit]:
        events.append({
            "id": f"cert-{c.id}", "student_name": _name(c.user), "course_name": c.course.title,
            "activity_type": "certificate", "content": "A obtenu son certificat",
            "timestamp": c.issue_date.isoformat(),
        })
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events[:limit]
