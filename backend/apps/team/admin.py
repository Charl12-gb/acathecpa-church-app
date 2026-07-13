from django.contrib import admin

from .models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "title", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("name", "title")
