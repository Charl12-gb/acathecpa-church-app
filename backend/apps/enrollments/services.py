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

from apps.courses.models import (
    Course,
    CourseLesson,
    CourseSection,
    CourseStatus,
    CourseTest,
)

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


def get_certificate_by_code(code: str) -> Optional[Certificate]:
    return (
        Certificate.objects.filter(verification_code=code)
        .select_related("course", "user")
        .first()
    )


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
    """Share of the course's lessons done and quizzes passed."""
    lesson_ids = set(
        CourseLesson.objects.filter(section__course_id=enrollment.course_id).values_list("id", flat=True)
    )
    test_ids = set(
        CourseTest.objects.filter(section__course_id=enrollment.course_id, questions__isnull=False)
        .values_list("id", flat=True)
        .distinct()
    )
    total = len(lesson_ids) + len(test_ids)
    if total == 0:
        return 0.0
    done = len(lesson_ids & set(enrollment.completed_lessons or [])) + len(
        test_ids & _passed_test_ids(enrollment)
    )
    return round(done / total * 100, 1)


def _passed_test_ids(enrollment: Enrollment) -> set:
    return {
        a.get("test_id") for a in (enrollment.test_attempts or []) if a.get("passed")
    }


def _section_is_complete(section, completed_lesson_ids: set, passed_test_ids: set) -> bool:
    """A section is done when every lesson is done and its quiz (if any) is passed."""
    if not {l.id for l in section.lessons.all()}.issubset(completed_lesson_ids):
        return False
    test = getattr(section, "test", None)
    if test is not None and test.questions.exists() and test.id not in passed_test_ids:
        return False
    return True


def auto_complete_sections(enrollment: Enrollment, course_id: int) -> bool:
    """Mark sections as completed when their lessons are done and quiz passed."""
    course = (
        Course.objects.filter(pk=course_id)
        .prefetch_related("sections__lessons", "sections__test")
        .first()
    )
    if not course:
        return False

    completed_lesson_ids = set(enrollment.completed_lessons or [])
    completed_section_ids = set(enrollment.completed_sections or [])
    passed_test_ids = _passed_test_ids(enrollment)
    changed = False

    for section in course.sections.all():
        if section.id in completed_section_ids:
            continue
        if _section_is_complete(section, completed_lesson_ids, passed_test_ids):
            completed_section_ids.add(section.id)
            changed = True

    if changed:
        enrollment.completed_sections = list(completed_section_ids)
    return changed


def mark_lesson_completed(
    user_id: int, course_id: int, lesson_id: int
) -> Union[Enrollment, str, None]:
    enrollment = get_enrollment(user_id, course_id)
    if not enrollment:
        return None
    if not CourseLesson.objects.filter(pk=lesson_id, section__course_id=course_id).exists():
        return "LessonNotInCourse"

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
) -> Union[Enrollment, str, None]:
    """Complete a section only if its lessons are done and its quiz passed."""
    enrollment = get_enrollment(user_id, course_id)
    if not enrollment:
        return None

    section = (
        CourseSection.objects.filter(pk=section_id, course_id=course_id)
        .prefetch_related("lessons")
        .select_related("test")
        .first()
    )
    if not section:
        return "SectionNotInCourse"

    if section_id in (enrollment.completed_sections or []):
        return enrollment

    if not _section_is_complete(
        section, set(enrollment.completed_lessons or []), _passed_test_ids(enrollment)
    ):
        return "SectionNotFinished"

    enrollment.completed_sections = list(enrollment.completed_sections or []) + [section_id]
    enrollment.progress_percentage = _calculate_progress_percentage(enrollment)
    enrollment.save()
    return enrollment


def get_course_test(course_id: int, test_id: int) -> Optional[CourseTest]:
    return (
        CourseTest.objects.filter(pk=test_id, section__course_id=course_id)
        .prefetch_related("questions")
        .first()
    )


def _chosen_option(options: list, answer):
    """Resolve an answer (option text or option index) to the option dict."""
    if isinstance(answer, bool) or answer is None:
        return None
    if isinstance(answer, int):
        return options[answer] if 0 <= answer < len(options) else None
    for opt in options:
        if isinstance(opt, dict) and opt.get("text") == answer:
            return opt
    return None


def grade_test(test: CourseTest, answers: dict) -> dict:
    """
    Grade a submission on the server.

    ``answers`` maps question id -> chosen option (text or index). Questions
    without any correct option (open questions) cannot be auto-graded and are
    left out of the score.
    """
    earned = 0.0
    possible = 0.0
    summary = []
    for q in test.questions.all():
        options = [o for o in (q.options or []) if isinstance(o, dict)]
        if not any(o.get("is_correct") for o in options):
            continue
        points = q.points or 0
        possible += points
        chosen = _chosen_option(options, answers.get(q.id))
        correct = bool(chosen and chosen.get("is_correct"))
        if correct:
            earned += points
        summary.append(
            {"question_id": q.id, "is_correct": correct, "points_earned": points if correct else 0}
        )

    score = round(earned / possible * 100, 2) if possible else 100.0
    passing = test.passing_score if test.passing_score is not None else 70
    return {
        "score": score,
        "passed": score >= passing,
        "points_earned": earned,
        "points_possible": possible,
        "questions_summary": summary,
    }


def count_attempts(enrollment: Enrollment, test_id: int) -> int:
    return sum(1 for a in (enrollment.test_attempts or []) if a.get("test_id") == test_id)


def record_test_attempt(
    user_id: int,
    course_id: int,
    test_id: int,
    answers: dict,
    attempted_at: Optional[datetime] = None,
) -> Union[Enrollment, str]:
    enrollment = get_enrollment(user_id, course_id)
    if not enrollment:
        return "NotEnrolled"

    test = get_course_test(course_id, test_id)
    if not test:
        return "TestNotInCourse"

    attempt_number = count_attempts(enrollment, test_id) + 1
    if test.max_attempts and attempt_number > test.max_attempts:
        return "MaxAttemptsReached"

    result = grade_test(test, answers)
    attempted_at = attempted_at or timezone.now()
    attempt = {
        "test_id": test_id,
        "attempt_number": attempt_number,
        "score": result["score"],
        "passed": result["passed"],
        "points_earned": result["points_earned"],
        "points_possible": result["points_possible"],
        "attempted_at": attempted_at.isoformat(),
        "questions_summary": result["questions_summary"],
    }
    enrollment.test_attempts = list(enrollment.test_attempts or []) + [attempt]

    # Keep the best result per test
    scores = list(enrollment.test_scores or [])
    entry = {"test_id": test_id, "score": result["score"], "points": result["points_earned"]}
    for i, s in enumerate(scores):
        if s.get("test_id") == test_id:
            if result["score"] >= s.get("score", 0):
                scores[i] = entry
            break
    else:
        scores.append(entry)
    enrollment.test_scores = scores

    auto_complete_sections(enrollment, course_id)
    enrollment.progress_percentage = _calculate_progress_percentage(enrollment)
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

    from apps.courses.services import has_learning_content

    # Nothing to complete means nothing to certify.
    if not has_learning_content(course_id):
        return "CourseEmpty"

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
        total_points = sum(s.get("points", 0) for s in (enrollment.test_scores or []))
        if total_points < required_points:
            return f"PointsNotMet:{total_points}/{required_points}"

    cert = create_certificate(user_id=user_id, course_id=course_id)
    if not cert:
        return "CertificateCreationError"

    enrollment.completed_at = timezone.now()
    enrollment.progress_percentage = 100.0
    enrollment.save(update_fields=["completed_at", "progress_percentage"])
    return cert
