from rest_framework import serializers

from .models import Permission, Role, RolePermission, UserPermission


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "permission", "title", "category", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class RolePermissionSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    permission = PermissionSerializer(read_only=True)
    role_id = serializers.CharField(write_only=True)
    permission_id = serializers.CharField(write_only=True)

    class Meta:
        model = RolePermission
        fields = ("id", "role", "permission", "role_id", "permission_id", "created_at")
        read_only_fields = ("id", "created_at")


class UserPermissionSerializer(serializers.ModelSerializer):
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.CharField(write_only=True)

    class Meta:
        model = UserPermission
        fields = ("id", "user", "permission", "permission_id", "type", "created_at")
        read_only_fields = ("id", "created_at")
