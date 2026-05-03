from django.contrib import admin

from .models import LiveSession, LiveSessionAttendance


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "scheduled_for", "host", "course")
    list_filter = ("status",)
    search_fields = ("title", "meeting_room_name")
    raw_id_fields = ("host", "course")


@admin.register(LiveSessionAttendance)
class LiveSessionAttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "live_session", "user", "is_present", "join_count", "total_duration_seconds")
    list_filter = ("is_present",)
    raw_id_fields = ("live_session", "user")
