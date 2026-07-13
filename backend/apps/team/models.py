"""Team members shown in the public "Notre équipe" section, managed from admin."""
from django.db import models


class TeamMember(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, help_text="Fonction / rôle")
    photo_url = models.CharField(max_length=512, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    # e.g. {"linkedin": "...", "twitter": "...", "facebook": "...", "email": "..."}
    social_links = models.JSONField(default=dict, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "team_members"
        ordering = ["order", "id"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} — {self.title}"
