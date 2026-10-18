from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.models import AuditAction
from apps.audit.services import record

from .models import Permission, Role, RolePermission, UserPermission, UserRoleEnum
from .permissions import HasPermission
from .serializers import (
    PermissionSerializer,
    RolePermissionSerializer,
    RoleSerializer,
    UserPermissionSerializer,
)

# The application only knows these four roles (menus, hierarchy, checks by name).
SYSTEM_ROLES = {name for name, _ in UserRoleEnum.CHOICES}


class _PerActionPermissionMixin:
    """Each action requires its own named permission (read vs. write)."""

    action_permissions: dict = {}

    def get_permissions(self):
        name = self.action_permissions.get(self.action) or self.action_permissions["list"]
        return [IsAuthenticated(), HasPermission.with_name(name)()]


class RoleViewSet(_PerActionPermissionMixin, viewsets.ModelViewSet):
    """
    The four system roles are fixed: they cannot be created, renamed or deleted.
    A leftover custom role can only be deleted once nobody has it.
    """

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    action_permissions = {
        "list": "view_role", "retrieve": "view_role",
        "create": "create_role", "update": "edit_role", "partial_update": "edit_role",
        "destroy": "delete_role",
    }

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Les rôles sont fixes (étudiant, professeur, admin, super admin) : "
                       "ajustez plutôt leurs permissions."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        role = self.get_object()
        new_name = request.data.get("name", role.name)
        if role.name in SYSTEM_ROLES and new_name != role.name:
            return Response(
                {"detail": "Un rôle système ne peut pas être renommé."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        if role.name in SYSTEM_ROLES:
            return Response({"detail": "Un rôle système ne peut pas être supprimé."},
                            status=status.HTTP_400_BAD_REQUEST)
        if role.users.exists():
            return Response({"detail": "Ce rôle est encore attribué à des utilisateurs."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class PermissionViewSet(_PerActionPermissionMixin, viewsets.ReadOnlyModelViewSet):
    """Permissions are defined in code (that is where they are checked): read-only here."""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    action_permissions = {"list": "view_permission_def", "retrieve": "view_permission_def"}


class RolePermissionViewSet(
    _PerActionPermissionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = RolePermission.objects.select_related("role", "permission").all()
    serializer_class = RolePermissionSerializer
    action_permissions = {
        "list": "view_role", "retrieve": "view_role",
        "create": "assign_permission_to_role", "destroy": "remove_permission_from_role",
    }

    def create(self, request, *args, **kwargs):
        role = Role.objects.filter(pk=request.data.get("role_id")).first()
        perm = Permission.objects.filter(pk=request.data.get("permission_id")).first()
        if not role or not perm:
            raise ValidationError({"detail": "Rôle ou permission introuvable."})
        link, created = RolePermission.objects.get_or_create(role=role, permission=perm)
        if created:
            record(request.user, AuditAction.ROLE_PERMISSION_GRANTED, target_type="role",
                   target_id=role.id, target_label=role.name, permission=perm.permission)
        return Response(RolePermissionSerializer(link).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def perform_destroy(self, instance):
        record(self.request.user, AuditAction.ROLE_PERMISSION_REVOKED, target_type="role",
               target_id=instance.role_id, target_label=instance.role.name,
               permission=instance.permission.permission)
        instance.delete()


class UserPermissionViewSet(
    _PerActionPermissionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = UserPermission.objects.select_related("user", "permission").all()
    serializer_class = UserPermissionSerializer
    filterset_fields = ["user"]
    action_permissions = {
        "list": "view_user_permission_override", "retrieve": "view_user_permission_override",
        "create": "assign_user_permission_override", "destroy": "remove_user_permission_override",
    }

    def perform_create(self, serializer):
        user = serializer.validated_data["user"]
        perm = Permission.objects.filter(pk=serializer.validated_data.get("permission_id")).first()
        if not perm:
            raise ValidationError({"permission_id": "Permission introuvable."})
        kind = serializer.validated_data["type"]
        if UserPermission.objects.filter(user=user, permission=perm, type=kind).exists():
            raise ValidationError({"detail": "Cette dérogation existe déjà."})
        override = serializer.save(permission=perm)
        record(self.request.user, AuditAction.USER_PERMISSION_ADDED, target_type="user",
               target_id=user.id, target_label=user.email, permission=perm.permission, type=kind)
        return override

    def perform_destroy(self, instance):
        record(self.request.user, AuditAction.USER_PERMISSION_REMOVED, target_type="user",
               target_id=instance.user_id, target_label=instance.user.email,
               permission=instance.permission.permission, type=instance.type)
        instance.delete()
