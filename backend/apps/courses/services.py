"""
Business rules on a course as a whole: when it may be published or deleted,
and the instructor's view of its students.
"""
from __future__ import annotations

from typing import List, Optional

from django.db.models import Count, FloatField, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce

from .models import Course, CourseLesson, CourseTest


def has_learning_content(course_id: int) -> bool:
    """True when the course has at least one lesson or one quiz with questions."""
    return (
        CourseLesson.objects.filter(section__course_id=course_id).exists()
        or CourseTest.objects.filter(section__course_id=course_id, questions__isnull=False).exists()
    )


def publish_error(course: Course) -> Optional[str]:
    if not has_learning_content(course.id):
        return "Ajoutez au moins une leçon ou un quiz avant de publier ce cours."
    return None


def delete_error(course: Course) -> Optional[str]:
    """A course that students joined or paid for is kept for their records."""
    from apps.enrollments.models import Certificate, Enrollment
    from apps.payments.models import Payment

    if (
        Enrollment.objects.filter(course_id=course.id).exists()
        or Payment.objects.filter(course_id=course.id).exists()
        or Certificate.objects.filter(course_id=course.id).exists()
    ):
        return (
            "Ce cours a des étudiants inscrits, des paiements ou des certificats : "
            "il ne peut pas être supprimé. Repassez-le en brouillon pour le retirer du catalogue."
        )
    return None


def with_instructor_metrics(qs):
    """Annotate courses with their number of students and completed revenue."""
    from apps.payments.models import Payment, PaymentStatus

    revenue = (
        Payment.objects.filter(course_id=OuterRef("pk"), status=PaymentStatus.COMPLETED)
        .values("course_id")
        .annotate(total=Sum("amount"))
        .values("total")
    )
    return qs.annotate(
        students_count=Count("enrollments", distinct=True),
        revenue=Coalesce(Subquery(revenue, output_field=FloatField()), 0.0, output_field=FloatField()),
    )


def course_students(course: Course) -> List[dict]:
    """One row per enrolled student: progress, quiz results, certificate."""
    from apps.enrollments.models import Certificate, Enrollment

    tests = {
        t.id: t.title
        for t in CourseTest.objects.filter(section__course_id=course.id).order_by("section__order")
    }
    certificates = {
        c.user_id: c.verification_code
        for c in Certificate.objects.filter(course_id=course.id)
    }
    rows = []
    for e in Enrollment.objects.filter(course_id=course.id).select_related("user").order_by("-enrolled_at"):
        attempts = e.test_attempts or []
        quizzes = []
        for test_id, title in tests.items():
            mine = [a for a in attempts if a.get("test_id") == test_id]
            quizzes.append({
                "test_id": test_id,
                "title": title,
                "attempts": len(mine),
                "best_score": max((a.get("score", 0) for a in mine), default=None),
                "passed": any(a.get("passed") for a in mine),
            })
        last_activity = max(
            [e.enrolled_at.isoformat()] + [a.get("attempted_at") for a in attempts if a.get("attempted_at")]
            + ([e.completed_at.isoformat()] if e.completed_at else [])
        )
        rows.append({
            "user_id": e.user_id,
            "name": e.user.name or e.user.email.split("@")[0],
            "email": e.user.email,
            "enrolled_at": e.enrolled_at,
            "progress_percentage": e.progress_percentage,
            "completed_lessons": len(e.completed_lessons or []),
            "completed_at": e.completed_at,
            "last_activity": last_activity,
            "quizzes": quizzes,
            "certificate_code": certificates.get(e.user_id),
        })
    return rows
