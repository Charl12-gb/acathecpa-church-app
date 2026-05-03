"""
Service-level tests for enrollments + payment gate + progression + certificate.
"""
import pytest

from apps.courses.models import CourseStatus
from apps.enrollments.models import Certificate, Enrollment
from apps.enrollments.services import (
    check_and_issue_certificate,
    enroll_student_in_course,
    mark_lesson_completed,
    unenroll_student_from_course,
)
from apps.payments.models import Payment, PaymentStatus

pytestmark = pytest.mark.django_db


def test_enroll_in_free_published_course(student_user, free_published_course):
    result = enroll_student_in_course(free_published_course.id, student_user.id)
    assert isinstance(result, Enrollment)
    assert result.user_id == student_user.id


def test_enroll_in_unpublished_course_fails(student_user, draft_course):
    result = enroll_student_in_course(draft_course.id, student_user.id)
    assert result == "CourseNotPublished"


def test_enroll_in_unknown_course(student_user):
    assert enroll_student_in_course(999_999, student_user.id) == "NotFound"


def test_double_enrollment_fails(student_user, free_published_course):
    enroll_student_in_course(free_published_course.id, student_user.id)
    again = enroll_student_in_course(free_published_course.id, student_user.id)
    assert again == "AlreadyEnrolled"


def test_paid_course_blocks_without_payment(student_user, paid_published_course):
    result = enroll_student_in_course(paid_published_course.id, student_user.id)
    assert result == "PaymentRequired"


def test_paid_course_allowed_with_completed_payment(
    student_user, paid_published_course
):
    Payment.objects.create(
        user=student_user,
        course=paid_published_course,
        amount=paid_published_course.price,
        status=PaymentStatus.COMPLETED,
        transaction_ref="TXN-OK",
    )
    result = enroll_student_in_course(paid_published_course.id, student_user.id)
    assert isinstance(result, Enrollment)


def test_unenroll(student_user, enrollment, free_published_course):
    msg = unenroll_student_from_course(free_published_course.id, student_user.id)
    assert msg == "UnenrolledSuccessfully"
    assert not Enrollment.objects.filter(pk=enrollment.pk).exists()


def test_mark_lesson_completed_updates_progress(student_user, course_with_lessons):
    course = course_with_lessons["course"]
    lesson1, lesson2 = course_with_lessons["lessons"]
    enroll_student_in_course(course.id, student_user.id)

    enr = mark_lesson_completed(student_user.id, course.id, lesson1.id)
    assert lesson1.id in enr.completed_lessons
    assert enr.progress_percentage == 50.0

    enr = mark_lesson_completed(student_user.id, course.id, lesson2.id)
    assert enr.progress_percentage == 100.0
    # Section auto-completed
    section_id = course_with_lessons["section"].id
    assert section_id in enr.completed_sections


def test_mark_lesson_completed_idempotent(student_user, course_with_lessons):
    course = course_with_lessons["course"]
    lesson1 = course_with_lessons["lessons"][0]
    enroll_student_in_course(course.id, student_user.id)

    mark_lesson_completed(student_user.id, course.id, lesson1.id)
    enr = mark_lesson_completed(student_user.id, course.id, lesson1.id)
    assert enr.completed_lessons.count(lesson1.id) == 1


def test_certificate_requires_full_completion(student_user, course_with_lessons):
    course = course_with_lessons["course"]
    lesson1 = course_with_lessons["lessons"][0]
    enroll_student_in_course(course.id, student_user.id)
    mark_lesson_completed(student_user.id, course.id, lesson1.id)

    result = check_and_issue_certificate(student_user.id, course.id)
    assert result == "NotAllLessonsCompleted"


def test_certificate_issued_when_all_lessons_done(
    student_user, course_with_lessons
):
    course = course_with_lessons["course"]
    enroll_student_in_course(course.id, student_user.id)
    for lesson in course_with_lessons["lessons"]:
        mark_lesson_completed(student_user.id, course.id, lesson.id)

    result = check_and_issue_certificate(student_user.id, course.id)
    assert isinstance(result, Certificate)
    assert result.verification_code.startswith("CERT-")
