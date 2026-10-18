"""Service helpers for authentication & password reset."""
from __future__ import annotations

import hashlib
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


EMAIL_VERIFY_TOKEN_TYPE = "email_verify"
EMAIL_VERIFY_LIFETIME_MINUTES = 7 * 24 * 60


def _password_fingerprint(user: Optional[User]) -> str:
    """Changes whenever the password changes: makes reset links single-use."""
    return hashlib.sha256((user.password if user else "").encode()).hexdigest()[:16]


def _encode(payload: dict, lifetime_minutes: int) -> str:
    payload = {**payload, "exp": timezone.now() + timedelta(minutes=lifetime_minutes)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.SIMPLE_JWT["ALGORITHM"])


def _decode(token: str, token_type: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT["ALGORITHM"]])
    except jwt.PyJWTError:
        return None
    return payload if payload.get("type") == token_type else None


def generate_password_reset_token(email: str, lifetime_minutes: Optional[int] = None) -> str:
    return _encode(
        {"sub": email, "type": PASSWORD_RESET_TOKEN_TYPE, "pwd": _password_fingerprint(get_user_by_email(email))},
        lifetime_minutes or settings.PASSWORD_RESET_TOKEN_LIFETIME_MINUTES,
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    payload = _decode(token, PASSWORD_RESET_TOKEN_TYPE)
    if not payload:
        return None
    # Once the password has been changed, the link no longer works.
    if payload.get("pwd") != _password_fingerprint(get_user_by_email(payload.get("sub", ""))):
        return None
    return payload.get("sub")


def generate_email_verification_token(user: User) -> str:
    return _encode({"sub": user.email, "type": EMAIL_VERIFY_TOKEN_TYPE}, EMAIL_VERIFY_LIFETIME_MINUTES)


def verify_email_token(token: str) -> Optional[str]:
    payload = _decode(token, EMAIL_VERIFY_TOKEN_TYPE)
    return payload.get("sub") if payload else None


def send_verification_email(user: User) -> bool:
    token = generate_email_verification_token(user)
    return send_email(
        subject=f"Confirmez votre adresse email - {settings.PROJECT_NAME}",
        recipient=user.email,
        body=(
            f"Bonjour {user.name or ''},\n\n"
            f"Bienvenue sur {settings.PROJECT_NAME} ! Pour confirmer votre adresse email, ouvrez ce lien "
            "(valable 7 jours) :\n"
            f"{settings.FRONTEND_URL}/verify-email?token={token}\n\n"
            f"L'équipe {settings.PROJECT_NAME}"
        ),
    )


def send_email(
    *, subject: str, recipient: str, body: str, subtype: str = "plain",
    reply_to: Optional[str] = None,
) -> bool:
    """Lightweight wrapper around Django EmailMessage. Returns False if sending failed."""
    if not recipient:
        return False
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=f"{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>",
        to=[recipient],
        reply_to=[reply_to] if reply_to else None,
    )
    if subtype == "html":
        msg.content_subtype = "html"
    try:
        msg.send(fail_silently=False)
    except Exception as exc:  # noqa: BLE001
        logger.error("Error sending email to %s: %s", recipient, exc)
        return False
    return True
