from __future__ import annotations

from .models import AuditLog


def record(actor, action: str, *, target_type: str, target_id="", target_label: str = "", **details) -> AuditLog:
    """Write one audit entry. `details` must be JSON-serialisable."""
    return AuditLog.objects.create(
        actor=actor if getattr(actor, "pk", None) else None,
        actor_email=getattr(actor, "email", "") or "",
        action=action,
        target_type=target_type,
        target_id=str(target_id or ""),
        target_label=target_label[:255],
        details=details,
    )
