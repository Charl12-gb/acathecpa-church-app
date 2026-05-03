"""
Content endpoints (articles + podcasts).

Mounted at `/api/v1/contents/`.

    POST   /                  create_content
    GET    /                  view_any_content       (published only)
    GET    /user              view_own_content
    GET    /{id}/             view_content
    PUT    /{id}/             edit_own_content       (+ ownership)
    PATCH  /{id}/             edit_own_content       (+ ownership)
    DELETE /{id}/             delete_own_content     (+ ownership)
    POST   /{id}/publish/     publish_own_content    (+ ownership)
"""
from __future__ import annotations

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.permissions.permissions import HasPermission

from .models import Content, ContentStatus
from .serializers import ContentSerializer, ContentWriteSerializer


def _is_admin(user) -> bool:
    role = getattr(user, "role", None)
    return bool(role and role.name in ("admin", "super_admin"))


def _assert_can_edit(user, content: Content) -> None:
    if user.is_superuser or _is_admin(user):
        return
    if content.author_id == user.id:
        return
    raise PermissionDenied("Not authorized to modify this content.")


class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.select_related("author").all()

    permission_map = {
        "list": "view_any_content",
        "create": "create_content",
        "retrieve": "view_content",
        "update": "edit_own_content",
        "partial_update": "edit_own_content",
        "destroy": "delete_own_content",
        "publish": "publish_own_content",
        "user": "view_own_content",
    }

    filterset_fields = ["type", "status", "is_premium"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return ContentWriteSerializer
        return ContentSerializer

    def get_permissions(self):
        # Public read access for list/retrieve (anonymous users see published only).
        if self.action in {"list", "retrieve"}:
            return [AllowAny()]
        permission_classes = [IsAuthenticated]
        perm_name = self.permission_map.get(self.action)
        if perm_name:
            permission_classes.append(HasPermission.with_name(perm_name))
        return [p() for p in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            # Public listing: published only (mirrors FastAPI default)
            qs = qs.filter(status=ContentStatus.PUBLISHED)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        _assert_can_edit(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        _assert_can_edit(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        is_authed = user.is_authenticated
        is_owner = is_authed and user.id == instance.author_id
        is_admin = is_authed and _is_admin(user)

        # Drafts: only author or admin can view
        if instance.status == ContentStatus.DRAFT and not (is_owner or is_admin):
            raise PermissionDenied("This content is not published yet.")

        data = self.get_serializer(instance).data

        # Premium gate: redact body if user has not paid
        # Only the author bypasses (admins go through the admin space).
        if instance.is_premium and not is_owner:
            from apps.payments.services import has_completed_content_payment

            paid = is_authed and has_completed_content_payment(user.id, instance.id)
            if not paid:
                data["content_body"] = None
                data["media_url"] = None
                data["requires_payment"] = True
            else:
                data["requires_payment"] = False
        else:
            data["requires_payment"] = False

        return Response(data)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        content = self.get_object()
        _assert_can_edit(request.user, content)
        content.status = ContentStatus.PUBLISHED
        content.save(update_fields=["status", "updated_at"])
        return Response(ContentSerializer(content).data)

    @action(detail=False, methods=["get"], url_path="user")
    def user(self, request):
        status_filter = request.query_params.get("status")
        qs = Content.objects.filter(author=request.user).select_related("author")
        if status_filter:
            qs = qs.filter(status=status_filter)
        page = self.paginate_queryset(qs)
        serializer = ContentSerializer(page or qs, many=True)
        return (
            self.get_paginated_response(serializer.data)
            if page is not None
            else Response(serializer.data)
        )
