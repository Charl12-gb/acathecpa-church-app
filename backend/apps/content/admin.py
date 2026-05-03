from django.contrib import admin

from .models import Content


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "type", "status", "author", "is_premium", "created_at")
    list_filter = ("type", "status", "is_premium")
    search_fields = ("title", "description")
    raw_id_fields = ("author",)
