"""
Service layer for payments.

Includes :func:`has_completed_payment` which is used as the **payment gate**
by ``apps.enrollments.services.enroll_student_in_course`` (lazy import).
"""
from __future__ import annotations

import uuid
from typing import Optional

from django.utils import timezone

from .models import Payment, PaymentStatus


def create_payment(
    user_id: int,
    course_id: Optional[int] = None,
    amount: float = 0.0,
    currency: str = "XOF",
    payment_method: Optional[str] = None,
    *,
    content_id: Optional[int] = None,
) -> Payment:
    if bool(course_id) == bool(content_id):
        raise ValueError("Exactly one of course_id / content_id must be provided.")
    return Payment.objects.create(
        user_id=user_id,
        course_id=course_id,
        content_id=content_id,
        amount=amount,
        currency=currency,
        payment_method=payment_method,
        status=PaymentStatus.PENDING,
        transaction_ref=f"TXN-{uuid.uuid4().hex[:12].upper()}",
    )


def confirm_payment(payment_id: int, user_id: int) -> Optional[Payment]:
    payment = Payment.objects.filter(pk=payment_id, user_id=user_id).first()
    if not payment:
        return None
    if payment.status != PaymentStatus.PENDING:
        return payment
    payment.status = PaymentStatus.COMPLETED
    payment.completed_at = timezone.now()
    payment.save(update_fields=["status", "completed_at"])
    return payment


def get_payment_by_id(payment_id: int) -> Optional[Payment]:
    return (
        Payment.objects.filter(pk=payment_id)
        .select_related("course", "content")
        .first()
    )


def get_user_payments(user_id: int, skip: int = 0, limit: int = 50):
    qs = (
        Payment.objects.filter(user_id=user_id)
        .select_related("course", "content")
        .order_by("-created_at")
    )
    return list(qs[skip : skip + limit])


def has_completed_payment(user_id: int, course_id: int) -> bool:
    """Used by the enrollment service as a payment gate (course only)."""
    return Payment.objects.filter(
        user_id=user_id,
        course_id=course_id,
        status=PaymentStatus.COMPLETED,
    ).exists()


def has_completed_content_payment(user_id: int, content_id: int) -> bool:
    """Payment gate for premium articles/podcasts."""
    return Payment.objects.filter(
        user_id=user_id,
        content_id=content_id,
        status=PaymentStatus.COMPLETED,
    ).exists()
