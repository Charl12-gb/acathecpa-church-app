"""Tests for the student dashboard service + endpoint protection."""
import pytest

from apps.enrollments.models import Certificate
from apps.enrollments.services import enroll_student_in_course, mark_lesson_completed
from apps.student_dashboard import services as dashboard

pytestmark = pytest.mark.django_db


def test_stats_empty(student_user):
    stats = dashboard.get_dashboard_stats(student_user)
    assert stats["enrolled_courses_count"] == 0
    assert stats["certificates_count"] == 0
    assert stats["average_progress"] == 0


def test_stats_with_progress(student_user, course_with_lessons):
    course = course_with_lessons["course"]
    enroll_student_in_course(course.id, student_user.id)
    mark_lesson_completed(student_user.id, course.id, course_with_lessons["lessons"][0].id)

    stats = dashboard.get_dashboard_stats(student_user)
    assert stats["enrolled_courses_count"] == 1
    # 1 lesson done out of 2 -> 50%
    assert stats["average_progress"] == 50.0


def test_enrolled_courses_returns_progress(student_user, course_with_lessons):
    course = course_with_lessons["course"]
    enroll_student_in_course(course.id, student_user.id)
    mark_lesson_completed(student_user.id, course.id, course_with_lessons["lessons"][0].id)

    rows = dashboard.get_enrolled_courses(student_user)
    assert len(rows) == 1
    assert rows[0]["id"] == course.id
    assert rows[0]["progress"] == 50.0


def test_overall_progress(student_user, course_with_lessons):
    course = course_with_lessons["course"]
    enroll_student_in_course(course.id, student_user.id)
    mark_lesson_completed(student_user.id, course.id, course_with_lessons["lessons"][0].id)

    progress = dashboard.get_overall_progress(student_user)
    assert progress["completed_percentage"] == 50.0
    assert progress["in_progress_percentage"] == 50.0


def test_recommended_courses_excludes_enrolled(
    student_user, free_published_course, paid_published_course
):
    enroll_student_in_course(free_published_course.id, student_user.id)
    recos = dashboard.get_recommended_courses(student_user)
    enrolled_ids = {r["id"] for r in recos}
    assert free_published_course.id not in enrolled_ids
    assert paid_published_course.id in enrolled_ids


def test_recent_certificates(student_user, free_published_course):
    Certificate.objects.create(
        user=student_user,
        course=free_published_course,
        verification_code="CERT-XYZ12345",
    )
    recent = dashboard.get_recent_certificates(student_user)
    assert len(recent) == 1
    assert recent[0]["course_name"] == free_published_course.title


# --------------------------------------------------------------------------- #
# API access control
# --------------------------------------------------------------------------- #
def test_dashboard_stats_endpoint_for_student(auth_client, student_user):
    client = auth_client(student_user)
    resp = client.get("/api/v1/student/dashboard/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert "enrolled_courses_count" in body


def test_dashboard_forbidden_for_professor(auth_client, professor_user):
    client = auth_client(professor_user)
    resp = client.get("/api/v1/student/dashboard/stats")
    assert resp.status_code == 403


def test_dashboard_allowed_for_admin(auth_client, admin_user):
    client = auth_client(admin_user)
    resp = client.get("/api/v1/student/dashboard/stats")
    assert resp.status_code == 200
