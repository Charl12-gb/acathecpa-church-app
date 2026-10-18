"""Users CRUD endpoints (mirrors FastAPI `user_router`)."""
from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.permissions.models import Role
from apps.permissions.permissions import HasPermission

from . import hierarchy
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    list   -> view_any_user
    retrieve -> view_any_user_profile_detail
    update / partial_update -> edit_any_user_profile_detail
    destroy -> delete_any_user (cannot delete self)
    """
    queryset = User.objects.select_related("role", "professor_profile").all()

    permission_map = {
        "list": "view_any_user",
        "retrieve": "view_any_user_profile_detail",
        "update": "edit_any_user_profile_detail",
        "partial_update": "edit_any_user_profile_detail",
        "destroy": "delete_any_user",
        "deletion_impact": "delete_any_user",
    }

    filterset_fields = ["role__name", "is_active"]
    search_fields = ["email", "name", "phone"]
    ordering_fields = ["created_at", "email", "name"]

    def get_serializer_class(self):
        if self.action in {"update", "partial_update"}:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        perm_name = self.permission_map.get(self.action)
        permission_classes = [IsAuthenticated]
        if perm_name:
            permission_classes.append(HasPermission.with_name(perm_name))
        return [p() for p in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        if role and role.lower() != "all":
            qs = qs.filter(role__name=role)
        return qs

    def _requested_role_name(self, request):
        """Role asked for in an update, whether sent by name or by id."""
        role = request.data.get("role")
        if isinstance(role, dict):
            role = role.get("name")
        if not role and request.data.get("role_id"):
            found = Role.objects.filter(pk=request.data["role_id"]).first()
            role = found.name if found else None
        return role

    def update(self, request, *args, **kwargs):
        target = self.get_object()
        if not hierarchy.can_manage_user(request.user, target):
            raise PermissionDenied("Seul un super administrateur peut modifier ce compte.")
        if not hierarchy.can_assign_role(request.user, self._requested_role_name(request)):
            raise PermissionDenied("Seul un super administrateur peut attribuer ce rôle.")
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="deletion-impact")
    def deletion_impact(self, request, pk=None):
        """What a deletion would remove, and whether the caller may do it."""
        target = self.get_object()
        history = hierarchy.account_history(target)
        has_history = any(history.values())
        return Response({
            "history": history,
            "has_history": has_history,
            "can_delete": hierarchy.can_manage_user(request.user, target) and target.id != request.user.id
            and (not has_history or hierarchy.is_super_admin(request.user)),
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response(
                {"detail": "Vous ne pouvez pas supprimer votre propre compte."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not hierarchy.can_manage_user(request.user, instance):
            raise PermissionDenied("Seul un super administrateur peut supprimer ce compte.")
        data = UserSerializer(instance).data
        if hierarchy.is_super_admin(request.user):
            # Super admin: permanent deletion, data included.
            hierarchy.delete_account_with_data(instance)
            return Response(data)
        if any(hierarchy.account_history(instance).values()):
            return Response(
                {"detail": (
                    "Ce compte a un historique (inscriptions, paiements, certificats, cours ou contenus) : "
                    "désactivez-le plutôt. Seul un super administrateur peut le supprimer définitivement."
                )},
                status=status.HTTP_409_CONFLICT,
            )
        instance.delete()
        return Response(data)
