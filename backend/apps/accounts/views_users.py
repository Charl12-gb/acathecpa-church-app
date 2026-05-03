"""Users CRUD endpoints (mirrors FastAPI `user_router`)."""
from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.permissions.permissions import HasPermission

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return Response(
                {"detail": "Admins cannot delete their own account via this endpoint."},
                status=status.HTTP_403_FORBIDDEN,
            )
        data = UserSerializer(instance).data
        instance.delete()
        return Response(data)
