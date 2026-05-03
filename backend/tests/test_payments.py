"""Tests for the payments service layer."""
import pytest

from apps.payments.models import Payment, PaymentStatus
from apps.payments.services import (
    confirm_payment,
    create_payment,
    has_completed_payment,
)

pytestmark = pytest.mark.django_db


def test_create_payment_starts_pending(student_user, paid_published_course):
    payment = create_payment(
        student_user.id, paid_published_course.id, paid_published_course.price
    )
    assert payment.status == PaymentStatus.PENDING
    assert payment.transaction_ref.startswith("TXN-")


def test_confirm_payment_marks_completed(student_user, paid_published_course):
    payment = create_payment(
        student_user.id, paid_published_course.id, paid_published_course.price
    )
    confirmed = confirm_payment(payment.id, student_user.id)
    assert confirmed is not None
    assert confirmed.status == PaymentStatus.COMPLETED
    assert confirmed.completed_at is not None


def test_confirm_payment_unknown_returns_none(student_user):
    assert confirm_payment(999_999, student_user.id) is None


def test_confirm_payment_other_user_returns_none(
    student_user, professor_user, paid_published_course
):
    payment = create_payment(
        student_user.id, paid_published_course.id, paid_published_course.price
    )
    # Another user tries to confirm
    assert confirm_payment(payment.id, professor_user.id) is None


def test_has_completed_payment_true_after_confirm(
    student_user, paid_published_course
):
    payment = create_payment(
        student_user.id, paid_published_course.id, paid_published_course.price
    )
    assert has_completed_payment(student_user.id, paid_published_course.id) is False
    confirm_payment(payment.id, student_user.id)
    assert has_completed_payment(student_user.id, paid_published_course.id) is True


def test_has_completed_payment_false_when_only_pending(
    student_user, paid_published_course
):
    create_payment(student_user.id, paid_published_course.id, 5000.0)
    assert has_completed_payment(student_user.id, paid_published_course.id) is False
