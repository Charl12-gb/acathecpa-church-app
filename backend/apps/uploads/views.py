"""Generic file upload endpoint.

Accepts a multipart/form-data POST with a single ``file`` field, stores it
under MEDIA_ROOT/uploads/<category>/<uuid>.<ext> and returns a JSON
``{"url": "/media/uploads/...", "filename": "...", "size": N, "content_type": "..."}``.

The returned URL can then be persisted in the existing CharField columns
(``media_url``, ``video_url``, ``image_url`` …) without any schema change.
"""
from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# ─── allow-lists ──────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {
    "image":  {"jpg", "jpeg", "png", "gif", "webp", "svg", "avif"},
    "video":  {"mp4", "webm", "ogg", "mov", "m4v", "avi"},
    "audio":  {"mp3", "wav", "ogg", "m4a", "aac", "flac"},
    "document": {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "txt"},
}
MAX_SIZE_BYTES_BY_CATEGORY = {
    "image": 10 * 1024 * 1024,        # 10 MB
    "video": 500 * 1024 * 1024,       # 500 MB
    "audio": 100 * 1024 * 1024,       # 100 MB
    "document": 50 * 1024 * 1024,     # 50 MB
    "other": 50 * 1024 * 1024,
}

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]")


def _detect_category(extension: str) -> str:
    ext = extension.lower().lstrip(".")
    for category, exts in ALLOWED_EXTENSIONS.items():
        if ext in exts:
            return category
    return "other"


class UploadView(APIView):
    """``POST /api/v1/uploads/`` — multipart upload (authenticated only)."""

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        upload = request.FILES.get("file")
        if upload is None:
            return Response(
                {"detail": "Aucun fichier fourni (champ 'file' requis)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Optional client-provided category (image/video/audio/document); else auto-detect from ext
        client_category = (request.data.get("category") or "").strip().lower() or None

        original_name = upload.name or "file"
        ext = Path(original_name).suffix.lower().lstrip(".")
        detected_category = _detect_category(ext)
        category = client_category or detected_category

        if category not in ALLOWED_EXTENSIONS and category != "other":
            return Response(
                {"detail": f"Catégorie inconnue : {category}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_exts = ALLOWED_EXTENSIONS.get(category, set())
        if allowed_exts and ext not in allowed_exts:
            return Response(
                {
                    "detail": f"Extension '.{ext}' non autorisée pour la catégorie '{category}'.",
                    "allowed": sorted(allowed_exts),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_size = MAX_SIZE_BYTES_BY_CATEGORY.get(category, MAX_SIZE_BYTES_BY_CATEGORY["other"])
        if upload.size > max_size:
            return Response(
                {
                    "detail": (
                        f"Fichier trop volumineux ({upload.size} octets). "
                        f"Limite pour '{category}' : {max_size} octets."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        safe_stem = _SAFE_NAME_RE.sub("_", Path(original_name).stem)[:60] or "file"
        unique = uuid.uuid4().hex[:12]
        final_name = f"{safe_stem}-{unique}.{ext}" if ext else f"{safe_stem}-{unique}"
        relative_path = os.path.join("uploads", category, final_name)

        saved_path = default_storage.save(relative_path, upload)
        media_path = settings.MEDIA_URL + saved_path
        if not media_path.startswith("/"):
            media_path = "/" + media_path
        # Toujours renvoyer une URL absolue pour qu'elle soit directement
        # exploitable par <img>/<audio>/<video> sans transformation côté front.
        absolute_url = request.build_absolute_uri(media_path)

        return Response(
            {
                "url": absolute_url,
                "filename": final_name,
                "original_name": original_name,
                "size": upload.size,
                "content_type": upload.content_type,
                "category": category,
            },
            status=status.HTTP_201_CREATED,
        )
