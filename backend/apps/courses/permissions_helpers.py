"""
Ownership helpers for course-related resources.

Mirrors the FastAPI behaviour where the service layer returned "NotAuthorized"
when a non-owner (and non-admin) user tried to mutate a course/section/lesson/test.
"""
from __future__ import annotations

from rest_framework.exceptions import PermissionDenied


def _is_admin(user) -> bool:
    role = getattr(user, "role", None)
    return bool(role and role.name in ("admin", "super_admin"))


def assert_can_edit_course(user, course) -> None:
    if user.is_superuser or _is_admin(user):
        return
    if course.instructor_id == user.id:
        return
    raise PermissionDenied("Not authorized to modify this course.")


def assert_can_edit_section(user, section) -> None:
    assert_can_edit_course(user, section.course)


def assert_can_edit_lesson(user, lesson) -> None:
    assert_can_edit_section(user, lesson.section)


def assert_can_edit_test(user, test) -> None:
    if test.section_id is None:
        # Standalone tests: only admins (mirrors FastAPI fallback)
        if user.is_superuser or _is_admin(user):
            return
        raise PermissionDenied("Not authorized to modify this test.")
    assert_can_edit_section(user, test.section)


def assert_can_edit_question(user, question) -> None:
    assert_can_edit_test(user, question.test)
