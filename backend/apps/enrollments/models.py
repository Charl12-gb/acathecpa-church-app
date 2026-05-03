"""
Models for the `enrollments` app.

Mirrors the FastAPI models:
    - app/models/enrollments.py    -> Enrollment   (composite PK user_id + course_id)
    - app/models/certificate.py    -> Certificate

We keep the same DB table names (`enrollments`, `certificates`) so the
existing schema can be reused / migrated without renaming.
"""
from __future__ import annotations

import uuid
from django.conf import settings
from django.db import models


class Enrollment(models.Model):
    """One row per (user, course) pair."""

    # Django requires a primary key. Since Django doesn't directly support
    # composite primary keys in the ORM, we expose a synthetic auto pk and
    # enforce uniqueness on the (user, course) pair.
    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
        db_column="user_id",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
        db_column="course_id",
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress_percentage = models.FloatField(default=0.0)
    completed_at = models.DateTimeField(null=True, blank=True)

    completed_lessons = models.JSONField(default=list, blank=True)
    completed_sections = models.JSONField(default=list, blank=True)
    test_attempts = models.JSONField(default=list, blank=True)
    # [{"test_id": 1, "score": 80, "passed": true, "attempted_at": "...",
    #   "questions_summary": [...]}, ...]
    test_scores = models.JSONField(default=list, blank=True)
    # [{"test_id": 1, "score": 80}, ...]

    class Meta:
        db_table = "enrollments"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="uq_enrollment_user_course"
            )
        ]
        ordering = ["-enrolled_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Enrollment(user={self.user_id}, course={self.course_id})"


def _gen_verification_code() -> str:
    return f"CERT-{uuid.uuid4().hex[:10].upper()}"


class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates",
        db_column="user_id",
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="certificates",
        db_column="course_id",
    )
    issue_date = models.DateTimeField(auto_now_add=True)
    certificate_url = models.CharField(max_length=512, blank=True, null=True)
    verification_code = models.CharField(
        max_length=64, unique=True, blank=True, null=True, db_index=True
    )

    class Meta:
        db_table = "certificates"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"], name="uq_user_course_certificate"
            )
        ]
        ordering = ["-issue_date"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Certificate(user={self.user_id}, course={self.course_id})"
