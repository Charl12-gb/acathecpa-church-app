from django.contrib import admin

from .models import Certificate, Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "progress_percentage", "enrolled_at", "completed_at")
    list_filter = ("course",)
    search_fields = ("user__email", "course__title")
    raw_id_fields = ("user", "course")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "course", "issue_date", "verification_code")
    search_fields = ("verification_code", "user__email", "course__title")
    raw_id_fields = ("user", "course")
