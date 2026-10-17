"""
Jitsi as a Service (8x8 JaaS) tokens.

When JITSI_KID and JITSI_PRIVATE_KEY are configured, every participant gets
their own short-lived token, and only the host (or an admin) is moderator.
Otherwise the static JITSI_JWT from the settings is returned, as before:
whatever rights it carries are shared by everyone who joins.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import jwt
from django.conf import settings

TOKEN_LIFETIME_SECONDS = 3 * 60 * 60


def _private_key() -> str:
    key = settings.JITSI_PRIVATE_KEY
    if key and not key.lstrip().startswith("-----BEGIN") and Path(key).is_file():
        return Path(key).read_text()
    return key.replace("\\n", "\n")


def per_user_tokens_enabled() -> bool:
    return bool(settings.JITSI_APP_ID and settings.JITSI_KID and settings.JITSI_PRIVATE_KEY)


def token_for(user, room: str, moderator: bool) -> Optional[str]:
    if not per_user_tokens_enabled():
        return settings.JITSI_JWT or None
    now = int(time.time())
    payload = {
        "aud": "jitsi",
        "iss": "chat",
        "sub": settings.JITSI_APP_ID,
        "room": room,
        "iat": now,
        "nbf": now - 10,
        "exp": now + TOKEN_LIFETIME_SECONDS,
        "context": {
            "user": {
                "id": str(user.id),
                "name": user.name or user.email,
                "email": user.email,
                "moderator": "true" if moderator else "false",
            },
            "features": {
                "livestreaming": "false",
                "recording": "true" if moderator else "false",
                "transcription": "false",
                "outbound-call": "false",
            },
        },
    }
    return jwt.encode(payload, _private_key(), algorithm="RS256", headers={"kid": settings.JITSI_KID})
