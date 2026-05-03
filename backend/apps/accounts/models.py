"""
Custom User model + ProfessorProfile.

Matches the FastAPI/SQLAlchemy `users` and `professor_profiles` tables.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=32, unique=True, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    birthdate = models.CharField(max_length=32, blank=True, null=True)

    role = models.ForeignKey(
        "app_permissions.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        db_column="role_id",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return self.email or self.phone or f"User#{self.pk}"


class ProfessorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="professor_profile"
    )
    specialization = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    education = models.JSONField(default=list, blank=True)
    experience = models.JSONField(default=list, blank=True)
    skills = models.JSONField(default=list, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "professor_profiles"
