"""
Service layer for enrollment + progression + certificate logic.

Each function returns either a model instance, ``None``, or a sentinel string
(e.g. ``"PaymentRequired"``, ``"NotAllLessonsCompleted"``) that the view layer
maps to the appropriate HTTP error - mirroring the FastAPI behaviour.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Union

from django.db import transaction
from django.utils import timezone

from apps.courses.models import Course, CourseSection, CourseStatus

from .models import Certificate, Enrollment


# --------------------------------------------------------------------------- #
# Lookups
# --------------------------------------------------------------------------- #
def get_enrollment(user_id: int, course_id: int) -> Optional[Enrollment]:
    return Enrollment.objects.filter(user_id=user_id, course_id=course_id).first()


def get_user_enrolled_courses(user_id: int, skip: int = 0, limit: int = 100):
    qs = (
        Course.objects.filter(enrollments__user_id=user_id)
        .select_related("instructor")
        .order_by("-enrollments__enrolled_at")
    )
    return list(qs[skip : skip + limit])


def get_certificate_by_id(certificate_id: int) -> Optional[Certificate]:
    return Certificate.objects.filter(pk=certificate_id).select_related("course").first()


def get_certificate_for_course_by_user(
    user_id: int, course_id: int
) -> Optional[Certificate]:
    return Certificate.objects.filter(user_id=user_id, course_id=course_id).first()


def get_certificates_for_user(user_id: int, skip: int = 0, limit: int = 100):
    qs = (
        Certificate.objects.filter(user_id=user_id)
        .select_related("course")
        .order_by("-issue_date")
    )
    return list(qs[skip : skip + limit])


# --------------------------------------------------------------------------- #
# Enrollment lifecycle
# --------------------------------------------------------------------------- #
def _has_completed_payment(user_id: int, course_id: int) -> bool:
    """
    Stub for the payment gate. The `payments` app hasn't been migrated yet,
    so we lazily import it and degrade gracefully if absent.
    """
    try:
        from apps.payments.services import has_completed_payment  # type: ignore
    except Exception:
        return False
    return bool(has_completed_payment(user_id, course_id))


def enroll_student_in_course(
    course_id: int, user_id: int
) -> Union[Enrollment, str]:
    course = Course.objects.filter(pk=course_id).first()
    if not course:
        return "NotFound"
    if course.status != CourseStatus.PUBLISHED:
        return "CourseNotPublished"

    if get_enrollment(user_id, course_id):
        return "AlreadyEnrolled"

    if not course.is_free and (course.price is not None and course.price > 0):
        if not _has_completed_payment(user_id, course_id):
            return "PaymentRequired"

    enrollment = Enrollment.objects.create(user_id=user_id, course_id=course_id)
    return enrollment


def unenroll_student_from_course(course_id: int, user_id: int) -> str:
    enrollment = get_enrollment(user_id, course_id)
    if not enrollment:
        return "NotEnrolled"
    enrollment.delete()
    return "UnenrolledSuccessfully"


# --------------------------------------------------------------------------- #
# Progression
# --------------------------------------------------------------------------- #
def _calculate_progress_percentage(enrollment: Enrollment) -> float:
    course = (
        Course.objects.filter(pk=enrollment.course_id)
        .prefetch_related("sections__lessons")
        .first()
    )
    if not course:
        return 0.0
    total_lessons = sum(s.lessons.count() for s in course.sections.all())
    if total_lessons == 0:
        return 0.0
    completed = len(enrollment.completed_lessons or [])
    return min(round((completed / total_lessons) * 100, 1), 100.0)


def auto_complete_sections(enrollment: Enrollment, course_id: int) -> bool:
    """Mark sections as completed when all of their lessons are done."""
    course = (
        Course.objects.filter(pk=course_id)
        .prefetch_related("sections__lessons")
        .first()
    )
    if not course:
        return False

    completed_lesson_ids = set(enrollment.completed_lessons or [])
    completed_section_ids = set(enrollment.completed_sections or [])
    changed = False

    for section in course.sections.all():
        if section.id in completed_section_ids:
            continue
        section_lesson_ids = {l.id for l in section.lessons.all()}
        if section_lesson_ids and section_lesson_ids.issubset(completed_lesson_ids):
            completed_section_ids.add(section.id)
            changed = True

    if changed:
        enrollment.completed_sections = list(completed_section_ids)
    return changed


def mark_lesson_completed(
    user_id: int, course_id: int, lesson_id: int
) -> Optional[Enrollment]:
    enrollment = get_enrollment(user_id, course_id)
    if not enrollment:
        return None

    if lesson_id in (enrollment.completed_lessons or []):
        return enrollment

    new_lessons = list(enrollment.completed_lessons or [])
    new_lessons.append(lesson_id)
    enrollment.completed_lessons = new_lessons

    auto_complete_sections(enrollment, course_id)
    enrollment.progress_percentage = _calculate_progress_percentage(enrollment)
    enrollment.save()
    return enrollment


def mark_section_completed(
    user_id: int, course_id: int, section_id: int
) -> Optional[Enrollment]:
    enrollment = get_enrollment(user_id, course_id)
    if not enrollment:
        return None

    if section_id in (enrollment.completed_sections or []):
        return enrollment

    new_sections = list(enrollment.completed_sections or [])
    new_sections.append(section_id)
    enrollment.completed_sections = new_sections
    enrollment.progress_percentage = _calculate_progress_percentage(enrollment)
    enrollment.save()
    return enrollment


def record_test_attempt(
    user_id: int,
    course_id: int,
    test_id: int,
    score: float,
    passed: bool,
    questions_summary: list,
    attempted_at: Optional[datetime] = None,
) -> Optional[Enrollment]:
    enrollment = get_enrollment(user_id, course_id)
    if not enrollment:
        return None

    attempted_at = attempted_at or timezone.now()
    attempt = {
        "test_id": test_id,
        "score": score,
        "passed": passed,
        "attempted_at": attempted_at.isoformat(),
        "questions_summary": questions_summary or [],
    }
    enrollment.test_attempts = list(enrollment.test_attempts or []) + [attempt]

    # Keep latest score per test
    scores = list(enrollment.test_scores or [])
    score_entry = {"test_id": test_id, "score": score}
    for i, s in enumerate(scores):
        if s.get("test_id") == test_id:
            scores[i] = score_entry
            break
    else:
        scores.append(score_entry)
    enrollment.test_scores = scores

    enrollment.save()
    return enrollment


# --------------------------------------------------------------------------- #
# Certificate logic
# --------------------------------------------------------------------------- #
def _gen_verification_code() -> str:
    return f"CERT-{uuid.uuid4().hex[:10].upper()}"


def create_certificate(
    user_id: int,
    course_id: int,
    issue_date: Optional[datetime] = None,
) -> Optional[Certificate]:
    existing = get_certificate_for_course_by_user(user_id, course_id)
    if existing:
        return existing

    code = _gen_verification_code()
    return Certificate.objects.create(
        user_id=user_id,
        course_id=course_id,
        issue_date=issue_date or timezone.now(),
        verification_code=code,
        certificate_url=f"/certificates/verify/{code}",
    )


@transaction.atomic
def check_and_issue_certificate(
    user_id: int, course_id: int
) -> Union[Certificate, str]:
    enrollment = get_enrollment(user_id, course_id)
    if not enrollment:
        return "EnrollmentNotFound"

    course = (
        Course.objects.filter(pk=course_id)
        .prefetch_related("sections__lessons", "sections__test")
        .first()
    )
    if not course:
        return "CourseNotFound"

    if get_certificate_for_course_by_user(user_id, course_id):
        return "CertificateAlreadyIssued"

    # All lessons completed?
    all_lesson_ids = {l.id for s in course.sections.all() for l in s.lessons.all()}
    completed_lessons = set(enrollment.completed_lessons or [])
    if not all_lesson_ids.issubset(completed_lessons):
        return "NotAllLessonsCompleted"

    # Auto-complete sections then verify
    auto_complete_sections(enrollment, course_id)
    enrollment.save(update_fields=["completed_sections"])

    all_section_ids = {s.id for s in course.sections.all()}
    if not all_section_ids.issubset(set(enrollment.completed_sections or [])):
        return "NotAllSectionsCompleted"

    # Points required ?
    required_points = course.points_required_for_certificate
    if required_points and required_points > 0:
        total_points = sum(s.get("score", 0) for s in (enrollment.test_scores or []))
        if total_points < required_points:
            return f"PointsNotMet:{total_points}/{required_points}"

    cert = create_certificate(user_id=user_id, course_id=course_id)
    if not cert:
        return "CertificateCreationError"

    enrollment.completed_at = timezone.now()
    enrollment.progress_percentage = 100.0
    enrollment.save(update_fields=["completed_at", "progress_percentage"])
    return cert
