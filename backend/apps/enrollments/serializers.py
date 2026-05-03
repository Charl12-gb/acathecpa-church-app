from __future__ import annotations

from rest_framework import serializers

from .models import Certificate, Enrollment


# --------------------------------------------------------------------------- #
# Test attempts (nested in Enrollment)
# --------------------------------------------------------------------------- #
class TestAttemptQuestionSummarySerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    is_correct = serializers.BooleanField(required=False, allow_null=True)
    points_earned = serializers.FloatField(required=False, allow_null=True)


class TestAttemptInputSerializer(serializers.Serializer):
    """Payload sent by the frontend when submitting a test attempt."""

    score = serializers.FloatField(min_value=0)
    passed = serializers.BooleanField()
    questions_summary = TestAttemptQuestionSummarySerializer(
        many=True, required=False, default=list
    )


# --------------------------------------------------------------------------- #
# Enrollment / Progress
# --------------------------------------------------------------------------- #
class EnrollmentProgressSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "user_id",
            "course_id",
            "enrolled_at",
            "completed_at",
            "progress_percentage",
            "completed_lessons",
            "completed_sections",
            "test_attempts",
            "test_scores",
        ]
        read_only_fields = fields


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = [
            "id",
            "user",
            "course",
            "enrolled_at",
            "progress_percentage",
            "completed_at",
        ]
        read_only_fields = fields


# --------------------------------------------------------------------------- #
# Certificates
# --------------------------------------------------------------------------- #
class CertificateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id",
            "user",
            "user_id",
            "course",
            "course_id",
            "issue_date",
            "certificate_url",
            "verification_code",
        ]
        read_only_fields = fields


class CertificateDisplaySerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_image_url = serializers.CharField(source="course.image_url", read_only=True, allow_null=True)

    class Meta:
        model = Certificate
        fields = [
            "id",
            "course_id",
            "course_title",
            "course_image_url",
            "issue_date",
            "certificate_url",
            "verification_code",
        ]
        read_only_fields = fields
