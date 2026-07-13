"""Public directory of alumni (certified, visible students)."""
from __future__ import annotations

from django.db.models import Count
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import User


class AlumniSerializer(serializers.ModelSerializer):
    """Public-safe representation — no email / phone exposed."""

    certificates_count = serializers.IntegerField(read_only=True)
    formations = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name", "country", "certificates_count", "formations")

    def get_formations(self, obj: User) -> list[str]:
        # Distinct titles of the courses the alumnus has been certified for.
        return sorted(
            {
                cert.course.title
                for cert in obj.certificates.all()
                if cert.course_id and cert.course.title
            }
        )


class AlumniListView(ListAPIView):
    """List students who hold at least one certificate and are visible."""

    permission_classes = [AllowAny]
    serializer_class = AlumniSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            User.objects.filter(
                role__name="student",
                is_visible=True,
                is_active=True,
                certificates__isnull=False,
            )
            .annotate(certificates_count=Count("certificates", distinct=True))
            .prefetch_related("certificates__course")
            .order_by("name")
            .distinct()
        )
