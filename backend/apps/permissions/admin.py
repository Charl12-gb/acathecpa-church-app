from django.contrib import admin

from .models import Permission, Role, RolePermission, UserPermission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("permission", "title", "category")
    list_filter = ("category",)
    search_fields = ("permission", "title")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "permission")
    list_select_related = ("role", "permission")


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ("user", "permission", "type")
    list_select_related = ("user", "permission")
    list_filter = ("type",)
