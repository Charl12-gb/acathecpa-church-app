"""Serializers for the professors module + admin/professor dashboards."""
from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import ProfessorProfile, User
from apps.accounts.serializers import (
    ProfessorProfileSerializer,
    UserSerializer,
)


# --------------------------------------------------------------------------- #
# Profile create/update payloads
# --------------------------------------------------------------------------- #
class ProfessorProfileCreateForExistingUserSerializer(serializers.ModelSerializer):
    specialization = serializers.CharField(min_length=1)

    class Meta:
        model = ProfessorProfile
        fields = (
            "specialization", "bio", "education", "experience", "skills", "social_links",
        )


class ProfessorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessorProfile
        fields = (
            "specialization", "bio", "education", "experience", "skills", "social_links",
        )
        extra_kwargs = {f: {"required": False} for f in fields}


class ProfessorUserAndProfileCreateSerializer(serializers.Serializer):
    """
    Flat payload to create both a `User` (with role=professor) and a
    `ProfessorProfile`. Mirrors FastAPI's `ProfessorUserAndProfileCreate`.
    """
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    country = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    birthdate = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # Profile fields
    specialization = serializers.CharField(min_length=1)
    bio = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    education = serializers.JSONField(required=False)
    experience = serializers.JSONField(required=False)
    skills = serializers.JSONField(required=False)
    social_links = serializers.JSONField(required=False)


# --------------------------------------------------------------------------- #
# Admin dashboard
# --------------------------------------------------------------------------- #
class AdminDashboardStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_professors = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    new_enrollments_last_month = serializers.IntegerField()


class ProfessorStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.CharField()
    courses_count = serializers.IntegerField()
    published_courses_count = serializers.IntegerField()
    students_count = serializers.IntegerField()
    active_students_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    specialization = serializers.CharField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    is_active = serializers.BooleanField()
    latest_course_published_at = serializers.CharField(allow_null=True)


class RecentActivitySerializer(serializers.Serializer):
    id = serializers.CharField()
    user_name = serializers.CharField()
    action = serializers.CharField()
    resource_name = serializers.CharField()
    timestamp = serializers.CharField()


class UserDistributionSerializer(serializers.Serializer):
    students_count = serializers.IntegerField()
    professors_count = serializers.IntegerField()
    admins_count = serializers.IntegerField()


class MonthlyRegistrationSerializer(serializers.Serializer):
    month = serializers.CharField()
    count = serializers.IntegerField()


# --------------------------------------------------------------------------- #
# Professor dashboard
# --------------------------------------------------------------------------- #
class ProfessorDashboardStatsSerializer(serializers.Serializer):
    published_courses_count = serializers.IntegerField()
    total_students_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    total_questions_count = serializers.IntegerField()


class CoursePerformanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    students_count = serializers.IntegerField()
    rating = serializers.FloatField()
    last_updated = serializers.CharField()


class StudentEngagementSerializer(serializers.Serializer):
    course_name = serializers.CharField()
    average_hours_spent = serializers.FloatField()


class StudentDistributionInProfessorCoursesSerializer(serializers.Serializer):
    active_students_count = serializers.IntegerField()
    inactive_students_count = serializers.IntegerField()
    completed_students_count = serializers.IntegerField()


class ProfessorRecentActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student_name = serializers.CharField()
    course_name = serializers.CharField()
    activity_type = serializers.CharField()
    content = serializers.CharField()
    timestamp = serializers.CharField()


__all__ = [
    "ProfessorProfileCreateForExistingUserSerializer",
    "ProfessorProfileUpdateSerializer",
    "ProfessorUserAndProfileCreateSerializer",
    "AdminDashboardStatsSerializer",
    "ProfessorStatsSerializer",
    "RecentActivitySerializer",
    "UserDistributionSerializer",
    "MonthlyRegistrationSerializer",
    "ProfessorDashboardStatsSerializer",
    "CoursePerformanceSerializer",
    "StudentEngagementSerializer",
    "StudentDistributionInProfessorCoursesSerializer",
    "ProfessorRecentActivitySerializer",
    "UserSerializer",
    "ProfessorProfileSerializer",
]
