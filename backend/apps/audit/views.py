from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.hierarchy import is_super_admin

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    action_label = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = AuditLog
        fields = ("id", "created_at", "actor_email", "action", "action_label",
                  "target_type", "target_id", "target_label", "details")


class AuditLogListView(APIView):
    """GET /audit-logs?action=&q=&limit= (super admins only)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_super_admin(request.user):
            raise PermissionDenied("Journal réservé aux super administrateurs.")
        qs = AuditLog.objects.all()
        if action := request.query_params.get("action"):
            qs = qs.filter(action=action)
        if q := request.query_params.get("q"):
            qs = qs.filter(Q(actor_email__icontains=q) | Q(target_label__icontains=q))
        limit = min(int(request.query_params.get("limit", 200)), 1000)
        return Response(AuditLogSerializer(qs[:limit], many=True).data)
