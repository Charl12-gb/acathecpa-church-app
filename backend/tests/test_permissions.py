"""
Tests for the permission resolution logic.

Covers:
    - admin / super_admin bypass
    - role-based grant
    - user-level Add override
    - user-level Remove override (cancels role grant)
    - unauthenticated user
"""
import pytest

from apps.accounts.models import User
from apps.permissions.models import (
    Permission,
    RolePermission,
    UserPermission,
    UserPermissionType,
)
from apps.permissions.permissions import check_permission


pytestmark = pytest.mark.django_db


@pytest.fixture
def perm_view(db):
    return Permission.objects.create(
        permission="view_dummy", title="View dummy", category="Test"
    )


def test_admin_bypass(admin_user, perm_view):
    assert check_permission(admin_user, "view_dummy") is True


def test_super_admin_bypass(super_admin_user, perm_view):
    assert check_permission(super_admin_user, "view_dummy") is True


def test_anonymous_user_denied(perm_view):
    class Anon:
        is_authenticated = False
        is_active = False
    assert check_permission(Anon(), "view_dummy") is False


def test_role_grant(student_user, perm_view):
    RolePermission.objects.create(role=student_user.role, permission=perm_view)
    assert check_permission(student_user, "view_dummy") is True


def test_user_add_override_when_role_lacks(student_user, perm_view):
    UserPermission.objects.create(
        user=student_user, permission=perm_view, type=UserPermissionType.ADD
    )
    assert check_permission(student_user, "view_dummy") is True


def test_user_remove_override_cancels_role_grant(student_user, perm_view):
    RolePermission.objects.create(role=student_user.role, permission=perm_view)
    UserPermission.objects.create(
        user=student_user, permission=perm_view, type=UserPermissionType.REMOVE
    )
    assert check_permission(student_user, "view_dummy") is False


def test_inactive_user_denied(student_user, perm_view):
    student_user.is_active = False
    student_user.save()
    assert check_permission(student_user, "view_dummy") is False


def test_unknown_permission_denied(student_user):
    assert check_permission(student_user, "non_existent_permission") is False
