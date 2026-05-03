from rest_framework import serializers


class StudentDashboardStatsSerializer(serializers.Serializer):
    enrolled_courses_count = serializers.IntegerField()
    certificates_count = serializers.IntegerField()
    total_study_hours = serializers.FloatField()
    average_progress = serializers.FloatField()


class EnrolledCourseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    progress = serializers.FloatField()
    last_activity_timestamp = serializers.CharField(allow_null=True)
    image_url = serializers.CharField()


class OverallProgressSerializer(serializers.Serializer):
    completed_percentage = serializers.FloatField()
    in_progress_percentage = serializers.FloatField()


class WeeklyActivitySerializer(serializers.Serializer):
    day_of_week = serializers.CharField()
    study_hours = serializers.FloatField()


class RecommendedCourseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    category = serializers.CharField(allow_null=True)
    instructor_name = serializers.CharField()
    duration_weeks = serializers.IntegerField()
    image_url = serializers.CharField()


class RecentCertificateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    course_name = serializers.CharField()
    date_obtained = serializers.CharField(allow_null=True)
