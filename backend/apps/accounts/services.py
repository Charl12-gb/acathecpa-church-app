"""Service helpers for authentication & password reset."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional

import jwt
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from .models import User

logger = logging.getLogger(__name__)

PASSWORD_RESET_TOKEN_TYPE = "password_reset"


def get_user_by_email(email: str) -> Optional[User]:
    return User.objects.filter(email__iexact=email).first()


def get_user_by_phone(phone: str) -> Optional[User]:
    return User.objects.filter(phone=phone).first()


def authenticate_user_flexible(username: str, password: str) -> Optional[User]:
    """Authenticate by email OR phone."""
    user = get_user_by_email(username) or get_user_by_phone(username)
    if not user or not user.check_password(password):
        return None
    return user


def generate_password_reset_token(email: str) -> str:
    lifetime = settings.PASSWORD_RESET_TOKEN_LIFETIME_MINUTES
    expire = timezone.now() + timedelta(minutes=lifetime)
    payload = {"sub": email, "exp": expire, "type": PASSWORD_RESET_TOKEN_TYPE}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.SIMPLE_JWT["ALGORITHM"])


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
        )
    except jwt.PyJWTError:
        return None
    if payload.get("type") != PASSWORD_RESET_TOKEN_TYPE:
        return None
    return payload.get("sub")


def send_email(*, subject: str, recipient: str, body: str, subtype: str = "plain") -> None:
    """Lightweight wrapper around Django EmailMessage."""
    if not recipient:
        return
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=f"{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>",
        to=[recipient],
    )
    if subtype == "html":
        msg.content_subtype = "html"
    try:
        msg.send(fail_silently=False)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error sending email to %s: %s", recipient, exc)
