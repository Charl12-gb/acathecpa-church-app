"""Tests for live_sessions services + a couple of API smoke tests."""
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.live_sessions.models import (
    LiveSession,
    LiveSessionAttendance,
    LiveSessionStatus,
)
from apps.live_sessions.services import (
    create_live_session,
    delete_live_session,
    get_attendance_summary,
    record_join,
    record_leave,
    update_live_session_status,
)

pytestmark = pytest.mark.django_db


def _payload(course_id=None, **overrides):
    base = {
        "course_id": course_id,
        "title": "Cours direct",
        "scheduled_for": timezone.now() + timedelta(hours=1),
        "duration_minutes": 60,
    }
    base.update(overrides)
    return base


def test_create_live_session_for_own_course(professor_user, free_published_course):
    result = create_live_session(_payload(free_published_course.id), professor_user.id)
    assert isinstance(result, LiveSession)
    assert result.host_id == professor_user.id
    assert result.meeting_room_name.startswith("live-session-")


def test_create_live_session_unknown_course(professor_user):
    result = create_live_session(_payload(course_id=999_999), professor_user.id)
    assert result == "CourseNotFound"


def test_create_live_session_not_authorized_to_host(
    student_user, free_published_course
):
    # student is not the instructor of this course and not admin
    result = create_live_session(_payload(free_published_course.id), student_user.id)
    assert result == "NotAuthorizedToHost"


def test_create_live_session_no_course_allowed(professor_user):
    result = create_live_session(_payload(course_id=None), professor_user.id)
    assert isinstance(result, LiveSession)


def test_status_transition_to_ended_closes_attendances(
    professor_user, free_published_course, student_user
):
    session = create_live_session(
        _payload(free_published_course.id, status=LiveSessionStatus.LIVE),
        professor_user.id,
    )
    record_join(session, student_user)

    update_live_session_status(session.id, LiveSessionStatus.ENDED, professor_user)

    attendance = LiveSessionAttendance.objects.get(
        live_session=session, user=student_user
    )
    assert attendance.is_present is False
    assert attendance.last_left_at is not None


def test_record_join_and_leave_accumulates_duration(
    professor_user, free_published_course, student_user
):
    session = create_live_session(
        _payload(free_published_course.id, status=LiveSessionStatus.LIVE),
        professor_user.id,
    )
    record_join(session, student_user)
    record_leave(session.id, student_user)

    attendance = LiveSessionAttendance.objects.get(
        live_session=session, user=student_user
    )
    assert attendance.is_present is False
    assert attendance.join_count == 1


def test_attendance_summary_counts_unique(
    professor_user, free_published_course, student_user
):
    session = create_live_session(
        _payload(free_published_course.id, status=LiveSessionStatus.LIVE),
        professor_user.id,
    )
    record_join(session, student_user)
    summary = get_attendance_summary(session.id)
    assert summary["unique_attendees"] == 1
    assert summary["present_count"] == 1
    assert summary["title"] == session.title


def test_delete_by_non_host_forbidden(
    professor_user, free_published_course, student_user
):
    session = create_live_session(_payload(free_published_course.id), professor_user.id)
    result = delete_live_session(session.id, student_user)
    assert result == "NotAuthorized"
    assert LiveSession.objects.filter(pk=session.id).exists()


# --------------------------------------------------------------------------- #
# API: join endpoint should 503 when JITSI_APP_ID is empty (test settings)
# --------------------------------------------------------------------------- #
def test_join_returns_503_when_jitsi_not_configured(
    auth_client, admin_user, free_published_course, professor_user
):
    session = create_live_session(_payload(free_published_course.id), professor_user.id)
    client = auth_client(admin_user)  # admin bypasses permission check
    resp = client.post(f"/api/v1/live-sessions/{session.id}/join")
    assert resp.status_code == 503


def test_join_returns_400_when_session_ended(
    auth_client, admin_user, free_published_course, professor_user, settings
):
    settings.JITSI_APP_ID = "fake-app-id"
    session = create_live_session(_payload(free_published_course.id), professor_user.id)
    session.status = LiveSessionStatus.ENDED
    session.save()
    client = auth_client(admin_user)
    resp = client.post(f"/api/v1/live-sessions/{session.id}/join")
    assert resp.status_code == 400


def test_leave_returns_404_for_unknown_session(auth_client, admin_user):
    client = auth_client(admin_user)
    resp = client.post("/api/v1/live-sessions/999999/leave")
    assert resp.status_code == 404
