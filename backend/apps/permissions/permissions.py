"""
Permission checking service + DRF permission class.

Equivalent to `backend/app/permissions/dependencies.py::check_permission` and
`RequirePermission` from the FastAPI backend.
"""
from __future__ import annotations

from rest_framework.permissions import BasePermission

from .models import Permission, RolePermission, UserPermission, UserPermissionType


SUPER_ADMIN_ONLY_PERMISSIONS = frozenset({
    "create_role", "edit_role", "delete_role",
    "assign_permission_to_role", "remove_permission_from_role",
    "create_permission_def", "edit_permission_def", "delete_permission_def",
    "assign_user_permission_override", "remove_user_permission_override",
})


def check_permission(user, permission_name: str) -> bool:
    """Return True if the user is allowed to perform `permission_name`."""
    if not user or not user.is_authenticated or not user.is_active:
        return False

    # Bypass: super_admin has every permission; admin has every permission
    # except managing roles and permissions, which stays with super admins.
    role = getattr(user, "role", None)
    if role and role.name == "super_admin":
        return True
    if role and role.name == "admin":
        return permission_name not in SUPER_ADMIN_ONLY_PERMISSIONS

    # Role-based grant
    if user.role_id:
        role_grant = RolePermission.objects.filter(
            role_id=user.role_id,
            permission__permission=permission_name,
        ).exists()
        if role_grant:
            removed = UserPermission.objects.filter(
                user=user,
                permission__permission=permission_name,
                type=UserPermissionType.REMOVE,
            ).exists()
            return not removed

    # Direct user grant
    added = UserPermission.objects.filter(
        user=user,
        permission__permission=permission_name,
        type=UserPermissionType.ADD,
    ).exists()
    if added:
        return True

    return False


class IsAdminRole(BasePermission):
    """Allow only users whose role is ``admin`` or ``super_admin``.

    Used for admin-managed resources (team members, course categories) where
    reads are public but writes are restricted to staff, without having to seed
    dedicated named permissions.
    """

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        role = getattr(user, "role", None)
        return bool(role and role.name in ("admin", "super_admin"))


class HasPermission(BasePermission):
    """
    Usage::

        permission_classes = [IsAuthenticated, HasPermission.with_name("view_any_user")]
    """
    permission_name: str | None = None

    @classmethod
    def with_name(cls, permission_name: str) -> type["HasPermission"]:
        return type(
            f"HasPermission_{permission_name}",
            (cls,),
            {"permission_name": permission_name},
        )

    def has_permission(self, request, view) -> bool:
        name = self.permission_name or getattr(view, "required_permission", None)
        if name is None:
            return True
        return check_permission(request.user, name)
