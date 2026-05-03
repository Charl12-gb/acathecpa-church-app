from __future__ import annotations

from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Content


class ContentSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(read_only=True)
    author_name = serializers.CharField(source="author.name", read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Content
        fields = [
            "id",
            "title",
            "description",
            "content_body",
            "type",
            "format",
            "media_url",
            "is_premium",
            "price",
            "status",
            "tags",
            "author",
            "author_id",
            "author_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "author_id", "author_name", "created_at", "updated_at"]


class ContentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            "title",
            "description",
            "content_body",
            "type",
            "format",
            "media_url",
            "is_premium",
            "price",
            "status",
            "tags",
        ]
