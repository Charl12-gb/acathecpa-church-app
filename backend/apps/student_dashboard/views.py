"""
Student dashboard endpoints (`/api/v1/student/dashboard/...`).

Mirrors backend/app/routers/student_router.py.
Access is restricted to users whose role is `student` (mirrors the FastAPI
`require_student` dependency).
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    EnrolledCourseSerializer,
    OverallProgressSerializer,
    RecentCertificateSerializer,
    RecommendedCourseSerializer,
    StudentDashboardStatsSerializer,
    WeeklyActivitySerializer,
)


class IsStudent(BasePermission):
    """Mirrors FastAPI's `require_student`. Admins are allowed too."""

    message = "Accès réservé aux étudiants."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        role = getattr(user, "role", None)
        role_name = getattr(role, "name", None) if role else None
        return role_name in {"student", "admin", "super_admin"}


class _BaseStudentView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]


class StatsView(_BaseStudentView):
    def get(self, request):
        data = services.get_dashboard_stats(request.user)
        return Response(StudentDashboardStatsSerializer(data).data)


class EnrolledCoursesView(_BaseStudentView):
    def get(self, request):
        data = services.get_enrolled_courses(request.user)
        return Response(EnrolledCourseSerializer(data, many=True).data)


class OverallProgressView(_BaseStudentView):
    def get(self, request):
        data = services.get_overall_progress(request.user)
        return Response(OverallProgressSerializer(data).data)


class WeeklyActivityView(_BaseStudentView):
    def get(self, request):
        data = services.get_weekly_activity(request.user)
        return Response(WeeklyActivitySerializer(data, many=True).data)


class RecommendedCoursesView(_BaseStudentView):
    def get(self, request):
        data = services.get_recommended_courses(request.user)
        return Response(RecommendedCourseSerializer(data, many=True).data)


class RecentCertificatesView(_BaseStudentView):
    def get(self, request):
        data = services.get_recent_certificates(request.user)
        return Response(RecentCertificateSerializer(data, many=True).data)
