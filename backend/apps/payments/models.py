"""
Models for the `payments` app.

Mirrors `backend/app/models/payment.py` (FastAPI). Same `payments` table.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class PaymentMethod(models.TextChoices):
    MOBILE_MONEY = "mobile_money", "Mobile Money"
    CARD = "card", "Card"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"


class Payment(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        db_column="user_id",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="payments",
        db_column="course_id",
        null=True,
        blank=True,
    )
    content = models.ForeignKey(
        "content.Content",
        on_delete=models.CASCADE,
        related_name="payments",
        db_column="content_id",
        null=True,
        blank=True,
    )
    amount = models.FloatField()
    currency = models.CharField(max_length=10, default="XOF")
    status = models.CharField(
        max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    payment_method = models.CharField(
        max_length=32, choices=PaymentMethod.choices, blank=True, null=True
    )
    transaction_ref = models.CharField(
        max_length=255, unique=True, blank=True, null=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(course__isnull=False, content__isnull=True)
                    | models.Q(course__isnull=True, content__isnull=False)
                ),
                name="payment_target_exactly_one",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        target = f"course={self.course_id}" if self.course_id else f"content={self.content_id}"
        return f"Payment(id={self.id}, user={self.user_id}, {target}, status={self.status})"
