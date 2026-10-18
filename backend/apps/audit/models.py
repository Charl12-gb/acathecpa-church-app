"""Journal of sensitive back-office actions (roles, permissions, accounts)."""
from django.conf import settings
from django.db import models


class AuditAction(models.TextChoices):
    USER_ROLE_CHANGED = "user.role_changed", "Changement de rôle"
    USER_DEACTIVATED = "user.deactivated", "Compte désactivé"
    USER_REACTIVATED = "user.reactivated", "Compte réactivé"
    USER_PASSWORD_RESET = "user.password_reset", "Mot de passe modifié par un administrateur"
    USER_DELETED = "user.deleted", "Compte supprimé"
    USER_DELETED_WITH_DATA = "user.deleted_with_data", "Compte supprimé définitivement avec ses données"
    ROLE_PERMISSION_GRANTED = "role.permission_granted", "Permission accordée à un rôle"
    ROLE_PERMISSION_REVOKED = "role.permission_revoked", "Permission retirée à un rôle"
    USER_PERMISSION_ADDED = "user.permission_override_added", "Dérogation ajoutée"
    USER_PERMISSION_REMOVED = "user.permission_override_removed", "Dérogation supprimée"


class AuditLog(models.Model):
    # The actor may be deleted later: keep their email as written.
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    actor_email = models.CharField(max_length=255, blank=True)
    action = models.CharField(max_length=64, choices=AuditAction.choices, db_index=True)
    target_type = models.CharField(max_length=32)
    target_id = models.CharField(max_length=64, blank=True)
    target_label = models.CharField(max_length=255, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.actor_email} {self.action} {self.target_label}"
