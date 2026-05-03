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


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission.with_name("view_role")]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission.with_name("view_permission_def")]


class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.select_related("role", "permission").all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission.with_name("assign_permission_to_role")]


class UserPermissionViewSet(viewsets.ModelViewSet):
    queryset = UserPermission.objects.select_related("user", "permission").all()
    serializer_class = UserPermissionSerializer
    permission_classes = [IsAuthenticated, HasPermission.with_name("view_user_permission_override")]
