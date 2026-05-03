"""Tests for the professors module (profiles + admin/professor dashboards)."""
from __future__ import annotations

import pytest

from apps.accounts.models import ProfessorProfile, User
from apps.courses.models import Course, CourseStatus
from apps.professors import services


# --------------------------------------------------------------------------- #
# Profile CRUD
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_create_professor_user_and_profile_creates_user_with_role(role_professor):
    payload = {
        "email": "newprof@test.local",
        "password": "Password123!",
        "name": "New Prof",
        "specialization": "Math",
        "bio": "Loves teaching",
    }
    user = services.create_professor_user_and_profile(payload)
    assert isinstance(user, User)
    assert user.role_id == role_professor.id
    assert user.check_password("Password123!")
    assert user.professor_profile.specialization == "Math"


@pytest.mark.django_db
def test_create_professor_email_conflict(role_professor, professor_user):
    payload = {
        "email": professor_user.email,
        "password": "Password123!",
        "specialization": "Math",
    }
    assert services.create_professor_user_and_profile(payload) == "EmailAlreadyExists"


@pytest.mark.django_db
def test_add_profile_to_existing_user(student_user):
    payload = {"specialization": "Physics"}
    profile = services.add_profile_to_existing_user(student_user.id, payload)
    assert isinstance(profile, ProfessorProfile)
    # Adding twice -> conflict sentinel
    assert (
        services.add_profile_to_existing_user(student_user.id, payload)
        == "ProfileAlreadyExists"
    )


@pytest.mark.django_db
def test_update_and_delete_profile(professor_user):
    ProfessorProfile.objects.create(user=professor_user, specialization="Old")
    updated = services.update_profile(professor_user.id, {"specialization": "New"})
    assert updated.specialization == "New"
    deleted = services.delete_profile(professor_user.id)
    assert deleted is not None
    assert services.get_profile_by_user_id(professor_user.id) is None


# --------------------------------------------------------------------------- #
# Admin dashboard
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_admin_dashboard_stats(admin_user, professor_user, free_published_course):
    stats = services.get_admin_dashboard_stats()
    assert stats["total_users"] >= 2
    assert stats["total_professors"] == 1
    assert stats["total_courses"] == 1
    assert stats["new_enrollments_last_month"] >= 2  # parity: new users last 30d


@pytest.mark.django_db
def test_admin_user_distribution(
    admin_user, professor_user, student_user, super_admin_user
):
    dist = services.get_admin_user_distribution()
    assert dist["students_count"] == 1
    assert dist["professors_count"] == 1
    assert dist["admins_count"] == 2  # admin + super_admin


@pytest.mark.django_db
def test_admin_professors_lists_one(professor_user, free_published_course):
    rows = services.get_admin_professors()
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == professor_user.id
    assert row["courses_count"] == 1
    assert row["published_courses_count"] == 1


@pytest.mark.django_db
def test_admin_monthly_registrations_returns_six_months():
    months = services.get_admin_monthly_registrations()
    assert len(months) == 6
    for entry in months:
        assert "month" in entry and "count" in entry


@pytest.mark.django_db
def test_admin_dashboard_endpoint_requires_admin(
    auth_client, student_user, admin_user
):
    student_client = auth_client(student_user)
    assert student_client.get("/api/v1/admin/dashboard/stats").status_code == 403

    admin_client = auth_client(admin_user)
    res = admin_client.get("/api/v1/admin/dashboard/stats")
    assert res.status_code == 200
    assert "total_users" in res.json()


# --------------------------------------------------------------------------- #
# Professor dashboard
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_professor_dashboard_stats(professor_user, free_published_course, draft_course):
    stats = services.get_professor_dashboard_stats(professor_user)
    assert stats["published_courses_count"] == 1
    assert stats["total_questions_count"] == 0


@pytest.mark.django_db
def test_professor_dashboard_endpoint_requires_professor(
    auth_client, student_user, professor_user
):
    student_client = auth_client(student_user)
    assert student_client.get("/api/v1/professors/dashboard/stats").status_code == 403

    prof_client = auth_client(professor_user)
    res = prof_client.get("/api/v1/professors/dashboard/stats")
    assert res.status_code == 200


@pytest.mark.django_db
def test_professor_published_courses_endpoint(
    auth_client, professor_user, free_published_course, draft_course
):
    client = auth_client(professor_user)
    res = client.get("/api/v1/professors/dashboard/published-courses")
    assert res.status_code == 200
    titles = [c["title"] for c in res.json()]
    assert free_published_course.title in titles
    assert draft_course.title not in titles


# --------------------------------------------------------------------------- #
# Profile creation endpoint
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_create_professor_endpoint(auth_client, admin_user, role_professor):
    client = auth_client(admin_user)
    payload = {
        "email": "viaapi@test.local",
        "password": "Password123!",
        "name": "Via API",
        "specialization": "Chemistry",
    }
    res = client.post("/api/v1/professors/", payload, format="json")
    assert res.status_code == 201, res.content
    assert User.objects.filter(email="viaapi@test.local").exists()
