from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Permission, Role, RolePermission, UserPermission
from .permissions import HasPermission
from .serializers import (
    PermissionSerializer,
    RolePermissionSerializer,
    RoleSerializer,
    UserPermissionSerializer,
)


class _PerActionPermissionMixin:
    """Each action requires its own named permission (read vs. write)."""

    action_permissions: dict = {}

    def get_permissions(self):
        name = self.action_permissions.get(self.action) or self.action_permissions["list"]
        return [IsAuthenticated(), HasPermission.with_name(name)()]


class RoleViewSet(_PerActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    action_permissions = {
        "list": "view_role", "retrieve": "view_role",
        "create": "create_role", "update": "edit_role", "partial_update": "edit_role",
        "destroy": "delete_role",
    }


class PermissionViewSet(_PerActionPermissionMixin, viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    action_permissions = {
        "list": "view_permission_def", "retrieve": "view_permission_def",
        "create": "create_permission_def", "update": "edit_permission_def",
        "partial_update": "edit_permission_def", "destroy": "delete_permission_def",
    }


class RolePermissionViewSet(_PerActionPermissionMixin, viewsets.ModelViewSet):
    queryset = RolePermission.objects.select_related("role", "permission").all()
    serializer_class = RolePermissionSerializer
    action_permissions = {
        "list": "view_role", "retrieve": "view_role",
        "create": "assign_permission_to_role", "update": "assign_permission_to_role",
        "partial_update": "assign_permission_to_role", "destroy": "remove_permission_from_role",
    }


class UserPermissionViewSet(_PerActionPermissionMixin, viewsets.ModelViewSet):
    queryset = UserPermission.objects.select_related("user", "permission").all()
    serializer_class = UserPermissionSerializer
    action_permissions = {
        "list": "view_user_permission_override", "retrieve": "view_user_permission_override",
        "create": "assign_user_permission_override", "update": "assign_user_permission_override",
        "partial_update": "assign_user_permission_override", "destroy": "remove_user_permission_override",
    }
