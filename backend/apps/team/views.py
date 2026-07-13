from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.permissions.permissions import IsAdminRole

from .models import TeamMember
from .serializers import TeamMemberSerializer


class TeamMemberViewSet(viewsets.ModelViewSet):
    """Public read (active members); admin-only writes."""

    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    search_fields = ["name", "title"]
    ordering_fields = ["order", "name", "created_at"]

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminRole()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            user = self.request.user
            role = getattr(user, "role", None) if user and user.is_authenticated else None
            if not (role and role.name in ("admin", "super_admin")):
                qs = qs.filter(is_active=True)
        return qs
