"""
Roles, Permissions, RolesPermissions and UserPermissions models.

Mirrors the FastAPI/SQLAlchemy schema from `backend/app/permissions/models.py`
so the data model stays compatible.
"""
import uuid
from django.conf import settings
from django.db import models


class UserRoleEnum:
    """Canonical role names (mirrors FastAPI UserRoleEnum)."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PROFESSOR = "professor"
    STUDENT = "student"

    CHOICES = (
        (SUPER_ADMIN, "Super admin"),
        (ADMIN, "Admin"),
        (PROFESSOR, "Professor"),
        (STUDENT, "Student"),
    )


def _uuid_str() -> str:
    return str(uuid.uuid4())


class Role(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=_uuid_str, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Permission(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=_uuid_str, editable=False)
    permission = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permissions"
        ordering = ["category", "permission"]

    def __str__(self) -> str:
        return self.permission


class RolePermission(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=_uuid_str, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles_permissions"
        unique_together = (("role", "permission"),)


class UserPermissionType(models.TextChoices):
    ADD = "Add", "Add"
    REMOVE = "Remove", "Remove"


class UserPermission(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=_uuid_str, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_permissions_overrides",
    )
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="user_overrides")
    type = models.CharField(max_length=10, choices=UserPermissionType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_permissions"
        unique_together = (("user", "permission", "type"),)
