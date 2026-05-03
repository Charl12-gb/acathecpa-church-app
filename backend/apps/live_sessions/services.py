"""Service layer for live sessions + attendance tracking."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Union

from django.utils import timezone

from apps.courses.models import Course

from .models import LiveSession, LiveSessionAttendance, LiveSessionStatus


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _is_admin(user) -> bool:
    role = getattr(user, "role", None)
    return bool(role and role.name in ("admin", "super_admin"))


def _generate_meeting_room_name(course_id: Optional[int]) -> str:
    prefix = f"course_{course_id}" if course_id else "meet"
    return f"live-session-{prefix}-{uuid.uuid4().hex[:12]}"


def _duration_seconds(start: Optional[datetime], end: Optional[datetime] = None) -> int:
    if not start:
        return 0
    end = end or timezone.now()
    return max(int((end - start).total_seconds()), 0)


def _close_active_attendances(session: LiveSession, closed_at: datetime) -> None:
    for att in session.attendances.filter(is_present=True):
        if att.last_joined_at:
            att.total_duration_seconds = (att.total_duration_seconds or 0) + _duration_seconds(
                att.last_joined_at, closed_at
            )
        att.last_left_at = closed_at
        att.is_present = False
        att.save(update_fields=["total_duration_seconds", "last_left_at", "is_present"])


# --------------------------------------------------------------------------- #
# CRUD
# --------------------------------------------------------------------------- #
def create_live_session(
    payload: dict, host_id: int
) -> Union[LiveSession, str]:
    course_id = payload.get("course_id")
    if course_id:
        course = Course.objects.filter(pk=course_id).first()
        if not course:
            return "CourseNotFound"
        # Need the host instance for admin check
        from django.contrib.auth import get_user_model

        host = get_user_model().objects.filter(pk=host_id).select_related("role").first()
        if not host:
            return "HostUserNotFound"
        if course.instructor_id != host_id and not _is_admin(host):
            return "NotAuthorizedToHost"

    data = {k: v for k, v in payload.items() if k != "host_id"}
    if not data.get("meeting_room_name"):
        data["meeting_room_name"] = _generate_meeting_room_name(course_id)

    session = LiveSession.objects.create(host_id=host_id, **data)
    return session


def get_live_session(session_id: int) -> Optional[LiveSession]:
    return (
        LiveSession.objects.filter(pk=session_id)
        .select_related("host", "course")
        .first()
    )


def get_all_live_sessions(skip: int = 0, limit: int = 100):
    return list(
        LiveSession.objects.select_related("host", "course")
        .order_by("-scheduled_for")[skip : skip + limit]
    )


def get_live_sessions_for_host(host_id: int, skip: int = 0, limit: int = 100):
    return list(
        LiveSession.objects.filter(host_id=host_id)
        .select_related("host", "course")
        .order_by("-scheduled_for")[skip : skip + limit]
    )


def get_live_sessions_for_course(course_id: int, skip: int = 0, limit: int = 100):
    return list(
        LiveSession.objects.filter(course_id=course_id)
        .select_related("host", "course")
        .order_by("-scheduled_for")[skip : skip + limit]
    )


def update_live_session(
    session_id: int, payload: dict, current_user
) -> Union[LiveSession, str, None]:
    session = get_live_session(session_id)
    if not session:
        return None
    if session.host_id != current_user.id and not _is_admin(current_user):
        return "NotAuthorized"
    for field, value in payload.items():
        setattr(session, field, value)
    session.save()
    return session


def update_live_session_status(
    session_id: int, new_status: str, current_user
) -> Union[LiveSession, str, None]:
    session = get_live_session(session_id)
    if not session:
        return None
    if session.host_id != current_user.id and not _is_admin(current_user):
        return "NotAuthorized"

    now = timezone.now()
    if new_status == LiveSessionStatus.LIVE:
        session.actual_started_at = session.actual_started_at or now
        session.actual_ended_at = None
    elif new_status == LiveSessionStatus.ENDED:
        session.actual_started_at = session.actual_started_at or now
        session.actual_ended_at = now
        _close_active_attendances(session, now)

    session.status = new_status
    session.save()
    return session


def delete_live_session(
    session_id: int, current_user
) -> Union[LiveSession, str, None]:
    session = get_live_session(session_id)
    if not session:
        return None
    if session.host_id != current_user.id and not _is_admin(current_user):
        return "NotAuthorized"
    session.delete()
    return session


def reschedule_live_session(
    session_id: int, payload: dict, current_user
) -> Union[LiveSession, str, None]:
    """Create a NEW session cloned from the original, scheduled at a new date."""
    session = get_live_session(session_id)
    if not session:
        return None
    if session.host_id != current_user.id and not _is_admin(current_user):
        return "NotAuthorized"

    cloned = LiveSession.objects.create(
        course_id=session.course_id,
        title=payload.get("title") or session.title,
        description=payload.get("description")
        if payload.get("description") is not None
        else session.description,
        scheduled_for=payload["scheduled_for"],
        duration_minutes=payload.get("duration_minutes") or session.duration_minutes,
        host_id=session.host_id,
        status=LiveSessionStatus.SCHEDULED,
        meeting_room_name=_generate_meeting_room_name(session.course_id),
    )
    return cloned


# --------------------------------------------------------------------------- #
# Attendance
# --------------------------------------------------------------------------- #
def record_join(session: LiveSession, user) -> LiveSessionAttendance:
    now = timezone.now()
    attendance, created = LiveSessionAttendance.objects.get_or_create(
        live_session=session,
        user=user,
        defaults={
            "first_joined_at": now,
            "last_joined_at": now,
            "join_count": 1,
            "is_present": True,
        },
    )
    if not created and not attendance.is_present:
        attendance.first_joined_at = attendance.first_joined_at or now
        attendance.last_joined_at = now
        attendance.join_count = (attendance.join_count or 0) + 1
        attendance.is_present = True
        attendance.save()

    if session.status == LiveSessionStatus.LIVE and not session.actual_started_at:
        session.actual_started_at = now
        session.save(update_fields=["actual_started_at"])
    return attendance


def record_leave(session_id: int, user) -> Optional[LiveSessionAttendance]:
    attendance = LiveSessionAttendance.objects.filter(
        live_session_id=session_id, user=user
    ).first()
    if not attendance:
        return None
    if attendance.is_present and attendance.last_joined_at:
        now = timezone.now()
        attendance.total_duration_seconds = (
            attendance.total_duration_seconds or 0
        ) + _duration_seconds(attendance.last_joined_at, now)
        attendance.last_left_at = now
        attendance.is_present = False
        attendance.save()
    return attendance


def get_attendance_summary(session_id: int) -> Optional[dict]:
    session = (
        LiveSession.objects.filter(pk=session_id)
        .prefetch_related("attendances__user")
        .first()
    )
    if not session:
        return None

    expected_attendees = None
    if session.course_id:
        from apps.enrollments.models import Enrollment

        expected_attendees = Enrollment.objects.filter(course_id=session.course_id).count()

    attendees = []
    for att in sorted(
        session.attendances.all(),
        key=lambda r: r.first_joined_at or datetime.max.replace(tzinfo=None),
    ):
        total = att.total_duration_seconds or 0
        if att.is_present and att.last_joined_at:
            total += _duration_seconds(att.last_joined_at)
        attendees.append(
            {
                "user_id": att.user_id,
                "user_name": getattr(att.user, "name", None),
                "user_email": getattr(att.user, "email", None),
                "first_joined_at": att.first_joined_at,
                "last_joined_at": att.last_joined_at,
                "last_left_at": att.last_left_at,
                "total_duration_seconds": total,
                "join_count": att.join_count or 0,
                "is_present": att.is_present,
            }
        )

    unique = len(attendees)
    present = sum(1 for a in attendees if a["is_present"])
    rate = round((unique / expected_attendees) * 100, 2) if expected_attendees else None

    return {
        "session_id": session.id,
        "title": session.title,
        "status": session.status,
        "scheduled_for": session.scheduled_for,
        "planned_duration_minutes": session.duration_minutes,
        "actual_started_at": session.actual_started_at,
        "actual_ended_at": session.actual_ended_at,
        "actual_duration_seconds": _duration_seconds(
            session.actual_started_at, session.actual_ended_at
        ),
        "unique_attendees": unique,
        "present_count": present,
        "expected_attendees": expected_attendees,
        "attendance_rate": rate,
        "attendees": attendees,
    }
