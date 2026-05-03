"""
Shared pytest fixtures.

Provides roles, users (admin / professor / student), an API client and an
authenticated client that targets a chosen user via JWT.
"""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.courses.models import Course, CourseSection, CourseLesson, CourseStatus, LessonType
from apps.enrollments.models import Enrollment
from apps.permissions.models import Role


# --------------------------------------------------------------------------- #
# Roles
# --------------------------------------------------------------------------- #
@pytest.fixture
def role_admin(db):
    return Role.objects.create(name="admin")


@pytest.fixture
def role_super_admin(db):
    return Role.objects.create(name="super_admin")


@pytest.fixture
def role_professor(db):
    return Role.objects.create(name="professor")


@pytest.fixture
def role_student(db):
    return Role.objects.create(name="student")


# --------------------------------------------------------------------------- #
# Users
# --------------------------------------------------------------------------- #
def _make_user(email: str, role=None, **extra) -> User:
    user = User(email=email, name=extra.pop("name", email.split("@")[0]), **extra)
    user.set_password("Password123!")
    if role is not None:
        user.role = role
    user.save()
    return user


@pytest.fixture
def admin_user(db, role_admin):
    return _make_user("admin@test.local", role=role_admin)


@pytest.fixture
def super_admin_user(db, role_super_admin):
    return _make_user("super@test.local", role=role_super_admin)


@pytest.fixture
def professor_user(db, role_professor):
    return _make_user("prof@test.local", role=role_professor)


@pytest.fixture
def student_user(db, role_student):
    return _make_user("student@test.local", role=role_student)


# --------------------------------------------------------------------------- #
# API clients
# --------------------------------------------------------------------------- #
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client():
    """Return a callable that produces an authenticated APIClient for a user."""
    def _make(user):
        client = APIClient()
        token = RefreshToken.for_user(user).access_token
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client
    return _make


# --------------------------------------------------------------------------- #
# Course fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def free_published_course(professor_user):
    return Course.objects.create(
        title="Free Course",
        instructor=professor_user,
        status=CourseStatus.PUBLISHED,
        is_free=True,
        price=0.0,
    )


@pytest.fixture
def paid_published_course(professor_user):
    return Course.objects.create(
        title="Paid Course",
        instructor=professor_user,
        status=CourseStatus.PUBLISHED,
        is_free=False,
        price=5000.0,
    )


@pytest.fixture
def draft_course(professor_user):
    return Course.objects.create(
        title="Draft Course",
        instructor=professor_user,
        status=CourseStatus.DRAFT,
        is_free=True,
    )


@pytest.fixture
def course_with_lessons(free_published_course):
    """Free course with 1 section and 2 lessons."""
    section = CourseSection.objects.create(
        course=free_published_course, title="S1", order=1
    )
    lesson1 = CourseLesson.objects.create(
        section=section, title="L1", type=LessonType.TEXT, order=1
    )
    lesson2 = CourseLesson.objects.create(
        section=section, title="L2", type=LessonType.TEXT, order=2
    )
    return {
        "course": free_published_course,
        "section": section,
        "lessons": [lesson1, lesson2],
    }


@pytest.fixture
def enrollment(student_user, free_published_course):
    return Enrollment.objects.create(
        user=student_user, course=free_published_course
    )
