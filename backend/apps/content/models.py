"""
Models for the `content` app (articles + podcasts).

Mirrors `backend/app/models/content.py` (FastAPI). Uses lowercase enum values
to remain compatible with existing data.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models


class ContentType(models.TextChoices):
    ARTICLE = "article", "Article"
    PODCAST = "podcast", "Podcast"


class ContentFormat(models.TextChoices):
    AUDIO = "audio", "Audio"
    VIDEO = "video", "Video"
    TEXT = "text", "Text"
    PDF = "pdf", "PDF"


class ContentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class Content(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    content_body = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=16, choices=ContentType.choices)
    format = models.CharField(
        max_length=16, choices=ContentFormat.choices, blank=True, null=True
    )
    media_url = models.CharField(max_length=512, blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    price = models.FloatField(blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_content",
        db_column="author_id",
    )
    status = models.CharField(
        max_length=16, choices=ContentStatus.choices, default=ContentStatus.DRAFT
    )
    tags = models.JSONField(blank=True, null=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "contents"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Content(id={self.id}, title={self.title!r})"
