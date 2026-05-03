from __future__ import annotations

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import LiveSession, LiveSessionStatus


class LiveSessionSerializer(serializers.ModelSerializer):
    host_id = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField(read_only=True, allow_null=True)
    host_name = serializers.CharField(source="host.name", read_only=True)
    host = UserSerializer(read_only=True)

    class Meta:
        model = LiveSession
        fields = [
            "id",
            "title",
            "description",
            "scheduled_for",
            "duration_minutes",
            "status",
            "course_id",
            "host",
            "host_id",
            "host_name",
            "actual_started_at",
            "actual_ended_at",
            "meeting_room_name",
        ]
        read_only_fields = [
            "id",
            "host",
            "host_id",
            "course_id",
            "host_name",
            "actual_started_at",
            "actual_ended_at",
            "meeting_room_name",
        ]


class LiveSessionCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    scheduled_for = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=LiveSessionStatus.choices,
        required=False,
        default=LiveSessionStatus.SCHEDULED,
    )
    meeting_room_name = serializers.CharField(required=False, allow_null=True)


class LiveSessionUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    scheduled_for = serializers.DateTimeField(required=False)
    duration_minutes = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=LiveSessionStatus.choices, required=False)
    meeting_room_name = serializers.CharField(required=False, allow_null=True)


class LiveSessionStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=LiveSessionStatus.choices)


class LiveSessionRescheduleSerializer(serializers.Serializer):
    scheduled_for = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(required=False, allow_null=True)
    title = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class JitsiJoinResponseSerializer(serializers.Serializer):
    app_id = serializers.CharField()
    domain = serializers.CharField()
    room = serializers.CharField()
    url = serializers.CharField()
    jwt = serializers.CharField(allow_null=True)
    uid = serializers.IntegerField()
