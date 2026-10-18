from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor_email", "action", "target_label")
    list_filter = ("action",)
    search_fields = ("actor_email", "target_label")
    readonly_fields = [f.name for f in AuditLog._meta.fields]
