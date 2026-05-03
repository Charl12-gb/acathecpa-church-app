"""Authentication endpoints (register, login, refresh, forgot/reset password, me)."""
from __future__ import annotations

import logging
import re

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.permissions.permissions import HasPermission

from . import services
from .models import User
from .serializers import (
    ForgotPasswordSerializer,
    FlexibleLoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    TokenPairSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^\+?[1-9]\d{1,14}$")


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if user.email:
            try:
                user_name = user.name or user.email.split("@")[0]
                services.send_email(
                    subject=f"Welcome to {settings.PROJECT_NAME}!",
                    recipient=user.email,
                    body=(
                        f"Hi {user_name},\n\n"
                        f"Welcome to {settings.PROJECT_NAME}! We're glad to have you.\n\n"
                        f"Thanks,\nThe {settings.PROJECT_NAME} Team"
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Welcome email failed for %s: %s", user.email, exc)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """OAuth2-style login (form data: username + password). Username = email or phone."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FlexibleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = services.authenticate_user_flexible(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response(
                {"detail": "Incorrect email/phone or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"detail": "Inactive user"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(TokenPairSerializer.for_user(user))


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Accept refresh token from either request body (`refresh_token`) OR
        # `Authorization: Bearer <refresh_token>` header (frontend convention).
        token_value = request.data.get("refresh_token") if hasattr(request, "data") else None
        if not token_value:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.lower().startswith("bearer "):
                token_value = auth_header.split(" ", 1)[1].strip()
        if not token_value:
            return Response(
                {"detail": "Missing refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(token_value)
            user_id = refresh.payload.get("user_id")
        except (InvalidToken, TokenError):
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = User.objects.filter(pk=user_id, is_active=True).first()
        if not user:
            return Response(
                {"detail": "User not found or inactive"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(TokenPairSerializer.for_user(user))


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        user = services.get_user_by_email(email)
        if user and user.is_active:
            try:
                token = services.generate_password_reset_token(email=user.email)
                reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
                user_name = user.name or user.email.split("@")[0]
                services.send_email(
                    subject=f"Reset Your Password for {settings.PROJECT_NAME}",
                    recipient=user.email,
                    body=(
                        f"Hi {user_name},\n\n"
                        f"Someone requested a password reset for your account on {settings.PROJECT_NAME}.\n"
                        f"If this was you, click the link below to reset your password:\n{reset_url}\n\n"
                        "If you did not request this, please ignore this email. "
                        "This link will expire in 15 minutes.\n\n"
                        f"Thanks,\nThe {settings.PROJECT_NAME} Team"
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                logger.error("Forgot-password flow failed for %s: %s", email, exc)
        else:
            logger.info("Password reset requested for unknown/inactive: %s", email)

        return Response(
            {"message": "If an account with that email exists, a password reset link has been sent."}
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = services.verify_password_reset_token(serializer.validated_data["token"])
        if not email:
            return Response(
                {"detail": "Invalid or expired token. Please request a new password reset."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = services.get_user_by_email(email)
        if not user or not user.is_active:
            return Response(
                {"detail": "User not found or inactive. Cannot reset password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])

        try:
            user_name = user.name or user.email.split("@")[0]
            services.send_email(
                subject=f"Your Password for {settings.PROJECT_NAME} Has Been Changed",
                recipient=user.email,
                body=(
                    f"Hi {user_name},\n\n"
                    f"This is a confirmation that the password for your account on {settings.PROJECT_NAME} "
                    "has just been changed.\n\n"
                    "If you did not authorize this change, please contact support immediately.\n\n"
                    f"Thanks,\nThe {settings.PROJECT_NAME} Team"
                ),
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Password change confirmation email failed for %s: %s", user.email, exc)

        return Response(
            {"message": "Password updated successfully. You can now log in with your new password."}
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated, HasPermission.with_name("view_own_profile")]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ValidateUsernameView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username: str):
        is_email = bool(EMAIL_RE.match(username))
        is_phone = bool(PHONE_RE.match(username))
        if not (is_email or is_phone):
            return Response(
                {"detail": "Username must be a valid email or phone number"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"username": username, "type": "email" if is_email else "phone", "valid": True}
        )
