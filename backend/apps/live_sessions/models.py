"""
Models for the `live_sessions` app : LiveSession + LiveSessionAttendance.

Mirrors:
    - backend/app/models/live_session.py
    - backend/app/models/live_session_attendance.py
"""
from __future__ import annotations

from django.conf import settings
from django.db import models


class LiveSessionStatus(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    LIVE = "live", "Live"
    ENDED = "ended", "Ended"


class LiveSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        related_name="live_sessions",
        db_column="course_id",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    scheduled_for = models.DateTimeField()
    duration_minutes = models.IntegerField(blank=True, null=True)
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hosted_live_sessions",
        db_column="host_id",
    )
    status = models.CharField(
        max_length=16, choices=LiveSessionStatus.choices, default=LiveSessionStatus.SCHEDULED
    )
    actual_started_at = models.DateTimeField(blank=True, null=True)
    actual_ended_at = models.DateTimeField(blank=True, null=True)
    meeting_room_name = models.CharField(
        max_length=255, unique=True, blank=True, null=True
    )

    class Meta:
        db_table = "live_sessions"
        ordering = ["-scheduled_for"]


class LiveSessionAttendance(models.Model):
    id = models.BigAutoField(primary_key=True)
    live_session = models.ForeignKey(
        LiveSession,
        on_delete=models.CASCADE,
        related_name="attendances",
        db_column="live_session_id",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="live_session_attendances",
        db_column="user_id",
    )
    first_joined_at = models.DateTimeField(blank=True, null=True)
    last_joined_at = models.DateTimeField(blank=True, null=True)
    last_left_at = models.DateTimeField(blank=True, null=True)
    total_duration_seconds = models.IntegerField(default=0)
    join_count = models.IntegerField(default=0)
    is_present = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "live_session_attendances"
        constraints = [
            models.UniqueConstraint(
                fields=["live_session", "user"],
                name="uq_live_session_attendance_session_user",
            )
        ]
