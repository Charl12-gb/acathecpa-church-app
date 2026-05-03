from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "course", "amount", "currency", "status", "created_at", "completed_at")
    list_filter = ("status", "payment_method", "currency")
    search_fields = ("transaction_ref", "user__email", "course__title")
    raw_id_fields = ("user", "course")
