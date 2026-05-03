from __future__ import annotations

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.permissions.models import Role, UserRoleEnum
from apps.permissions.serializers import RoleSerializer

from .models import ProfessorProfile, User


# --------------------------------------------------------------------------- #
# Professor profile
# --------------------------------------------------------------------------- #
class ProfessorProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProfessorProfile
        fields = (
            "id", "user_id",
            "specialization", "bio", "education", "experience", "skills", "social_links",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "user_id", "created_at", "updated_at")


# --------------------------------------------------------------------------- #
# User read / write
# --------------------------------------------------------------------------- #
class UserSerializer(serializers.ModelSerializer):
    """Read serializer (mirrors FastAPI `User` schema)."""
    role = RoleSerializer(read_only=True)
    professor_profile = ProfessorProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "name", "phone", "country", "birthdate",
            "role", "is_active", "created_at", "updated_at",
            "professor_profile",
        )
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role_name = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("email", "name", "phone", "country", "birthdate", "password", "role_name", "role")

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        role_name = (
            validated_data.pop("role_name", None)
            or validated_data.pop("role", None)
            or UserRoleEnum.STUDENT
        )
        role = Role.objects.filter(name=role_name).first()

        user = User(role=role, **validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    role_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    role = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "email", "name", "phone", "country", "birthdate",
            "is_active", "password", "role_id", "role",
        )
        extra_kwargs = {f: {"required": False} for f in fields}

    def update(self, instance: User, validated_data: dict) -> User:
        password = validated_data.pop("password", None)
        role_id = validated_data.pop("role_id", serializers.empty)
        role_name = validated_data.pop("role", serializers.empty)
        if role_id is not serializers.empty:
            instance.role_id = role_id
        elif role_name is not serializers.empty and role_name:
            role_obj = Role.objects.filter(name=role_name).first()
            if role_obj is not None:
                instance.role = role_obj
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# --------------------------------------------------------------------------- #
# Auth: login, refresh, password reset
# --------------------------------------------------------------------------- #
class FlexibleLoginSerializer(serializers.Serializer):
    username = serializers.CharField()  # email or phone
    password = serializers.CharField(write_only=True)


class TokenPairSerializer(serializers.Serializer):
    """Response payload for /auth/login and /auth/token/refresh."""
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    token_type = serializers.CharField(default="bearer")
    user = UserSerializer()

    @staticmethod
    def for_user(user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "token_type": "bearer",
            "user": UserSerializer(user).data,
        }


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
