"""
Student dashboard service layer.

Important translation note vs the FastAPI source:
the original code reads `CourseLesson.is_completed` (a global flag).
In our Django port, lesson completion is per-user and lives in
`enrollments.Enrollment.completed_lessons` (JSON list of lesson IDs).
All queries below are adapted accordingly.
"""
from __future__ import annotations

from datetime import timedelta
from typing import List

from django.utils import timezone
from django.db.models import Q

from apps.courses.models import Course, CourseLesson
from apps.enrollments.models import Certificate, Enrollment


def _completed_count_for_user(user_id: int) -> int:
    total = 0
    for enrollment in Enrollment.objects.filter(user_id=user_id).only("completed_lessons"):
        total += len(enrollment.completed_lessons or [])
    return total


def _total_lessons_for_user(user_id: int) -> int:
    course_ids = list(
        Enrollment.objects.filter(user_id=user_id).values_list("course_id", flat=True)
    )
    if not course_ids:
        return 0
    return CourseLesson.objects.filter(section__course_id__in=course_ids).count()


# --------------------------------------------------------------------------- #
# Stats
# --------------------------------------------------------------------------- #
def get_dashboard_stats(user) -> dict:
    enrolled_count = Enrollment.objects.filter(user_id=user.id).count()
    certificates_count = Certificate.objects.filter(user_id=user.id).count()

    completed = _completed_count_for_user(user.id)
    total = _total_lessons_for_user(user.id)

    average_progress = (completed / total * 100) if total else 0
    total_study_hours = completed * 0.5  # heuristic: 30 min per lesson

    return {
        "enrolled_courses_count": enrolled_count,
        "certificates_count": certificates_count,
        "total_study_hours": round(total_study_hours, 1),
        "average_progress": round(average_progress, 1),
    }


# --------------------------------------------------------------------------- #
# Enrolled courses (with progress)
# --------------------------------------------------------------------------- #
def get_enrolled_courses(user) -> List[dict]:
    enrollments = (
        Enrollment.objects.filter(user_id=user.id)
        .select_related("course")
        .prefetch_related("course__sections__lessons")
    )

    out: List[dict] = []
    for enrollment in enrollments:
        course = enrollment.course
        if not course:
            continue
        total_lessons = sum(s.lessons.count() for s in course.sections.all())
        completed = len(enrollment.completed_lessons or [])
        progress = (completed / total_lessons * 100) if total_lessons else 0.0
        out.append(
            {
                "id": course.id,
                "title": course.title,
                "progress": round(progress, 1),
                "last_activity_timestamp": (
                    course.updated_at.isoformat() if course.updated_at else None
                ),
                "image_url": course.image_url
                or f"https://picsum.photos/seed/{course.id}/300/200",
            }
        )
    return out


# --------------------------------------------------------------------------- #
# Overall progress
# --------------------------------------------------------------------------- #
def get_overall_progress(user) -> dict:
    total = _total_lessons_for_user(user.id)
    completed = _completed_count_for_user(user.id)
    completed_pct = (completed / total * 100) if total else 0
    in_progress_pct = (100 - completed_pct) if total else 0
    return {
        "completed_percentage": round(completed_pct, 1),
        "in_progress_percentage": round(in_progress_pct, 1),
    }


# --------------------------------------------------------------------------- #
# Weekly activity
# --------------------------------------------------------------------------- #
def get_weekly_activity(user) -> List[dict]:
    """
    Approximation: we don't track per-lesson completion timestamps, so we use
    enrollment.enrolled_at / completed_at as proxies for activity on that day.
    """
    today = timezone.now().date()
    days_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    activities = []
    for i in range(7):
        day_date = today - timedelta(days=6 - i)
        # how many enrollments were created or completed that day
        touched = Enrollment.objects.filter(user_id=user.id).filter(
            Q(enrolled_at__date=day_date) | Q(completed_at__date=day_date)
        ).count()
        # heuristic: 0.5h per touched enrollment
        activities.append(
            {"day_of_week": days_labels[i], "study_hours": round(touched * 0.5, 1)}
        )
    return activities


# --------------------------------------------------------------------------- #
# Recommended courses
# --------------------------------------------------------------------------- #
def get_recommended_courses(user) -> List[dict]:
    enrolled_ids = Enrollment.objects.filter(user_id=user.id).values_list(
        "course_id", flat=True
    )
    courses = (
        Course.objects.exclude(id__in=list(enrolled_ids))
        .select_related("instructor")[:3]
    )
    return [
        {
            "id": c.id,
            "title": c.title,
            "category": c.category,
            "instructor_name": getattr(c.instructor, "name", "Instructor"),
            "duration_weeks": 6,
            "image_url": c.image_url or f"https://picsum.photos/seed/{c.id}/300/200",
        }
        for c in courses
    ]


# --------------------------------------------------------------------------- #
# Recent certificates
# --------------------------------------------------------------------------- #
def get_recent_certificates(user) -> List[dict]:
    certs = (
        Certificate.objects.filter(user_id=user.id)
        .select_related("course")
        .order_by("-issue_date")[:3]
    )
    return [
        {
            "id": cert.id,
            "course_name": cert.course.title if cert.course else "Unknown Course",
            "date_obtained": cert.issue_date.strftime("%Y-%m-%d")
            if cert.issue_date
            else None,
        }
        for cert in certs
    ]
