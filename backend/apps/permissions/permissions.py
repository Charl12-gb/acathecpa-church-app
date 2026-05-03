"""
Permission checking service + DRF permission class.

Equivalent to `backend/app/permissions/dependencies.py::check_permission` and
`RequirePermission` from the FastAPI backend.
"""
from __future__ import annotations

from rest_framework.permissions import BasePermission

from .models import Permission, RolePermission, UserPermission, UserPermissionType


def check_permission(user, permission_name: str) -> bool:
    """Return True if the user is allowed to perform `permission_name`."""
    if not user or not user.is_authenticated or not user.is_active:
        return False

    # Bypass: super_admin / admin have all permissions.
    role = getattr(user, "role", None)
    if role and role.name in ("super_admin", "admin"):
        return True

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
