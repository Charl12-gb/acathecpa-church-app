"""
Live session endpoints (`/api/v1/live-sessions/`).

    GET    /                        list (host's own; admins see all)
    POST   /                        create_live_session
    GET    /course/{course_id}      list per course
    GET    /{id}/                   detail
    PUT    /{id}/                   update (host or admin)
    DELETE /{id}/                   delete (host or admin)
    PATCH  /{id}/status             update status (scheduled/live/ended)
    POST   /{id}/reschedule         create a clone with a new schedule
    GET    /{id}/attendance         attendance summary
    POST   /{id}/join               Jitsi credentials + record join
    POST   /{id}/leave              record leave
"""
from __future__ import annotations

from django.conf import settings as dj_settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course
from apps.permissions.permissions import HasPermission

from . import services
from .models import LiveSessionStatus
from .serializers import (
    LiveSessionCreateSerializer,
    LiveSessionRescheduleSerializer,
    LiveSessionSerializer,
    LiveSessionStatusUpdateSerializer,
    LiveSessionUpdateSerializer,
)


def _is_admin(user) -> bool:
    role = getattr(user, "role", None)
    return bool(role and role.name in ("admin", "super_admin"))


def _string_to_response(result):
    """Translate a service-layer sentinel string to an HTTP error."""
    mapping = {
        "NotAuthorized": (
            status.HTTP_403_FORBIDDEN,
            "Not authorized for this live session.",
        ),
        "NotAuthorizedToHost": (
            status.HTTP_403_FORBIDDEN,
            "User not authorized to host sessions for this course.",
        ),
        "CourseNotFound": (status.HTTP_404_NOT_FOUND, "Course not found."),
        "HostUserNotFound": (status.HTTP_404_NOT_FOUND, "Host user not found."),
    }
    code, msg = mapping.get(result, (status.HTTP_400_BAD_REQUEST, result))
    return Response({"detail": msg}, status=code)


class LiveSessionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Permission for listing
        if not HasPermission.with_name("view_live_sessions_for_course")().has_permission(
            request, self
        ):
            self.permission_denied(request)

        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 50))
        if _is_admin(request.user):
            sessions = services.get_all_live_sessions(skip, limit)
        else:
            sessions = services.get_live_sessions_for_host(request.user.id, skip, limit)
        return Response(LiveSessionSerializer(sessions, many=True).data)

    def post(self, request):
        if not HasPermission.with_name("create_live_session")().has_permission(
            request, self
        ):
            self.permission_denied(request)

        serializer = LiveSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.create_live_session(serializer.validated_data, request.user.id)
        if isinstance(result, str):
            return _string_to_response(result)
        return Response(
            LiveSessionSerializer(result).data, status=status.HTTP_201_CREATED
        )


class LiveSessionsForCourseView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("view_live_sessions_for_course"),
    ]

    def get(self, request, course_id: int):
        if not Course.objects.filter(pk=course_id).exists():
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 20))
        sessions = services.get_live_sessions_for_course(course_id, skip, limit)
        return Response(LiveSessionSerializer(sessions, many=True).data)


class LiveSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _check_perm(self, request, perm: str):
        if not HasPermission.with_name(perm)().has_permission(request, self):
            self.permission_denied(request)

    def get(self, request, session_id: int):
        self._check_perm(request, "view_live_session_detail")
        session = services.get_live_session(session_id)
        if not session:
            return Response(
                {"detail": "Live session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(LiveSessionSerializer(session).data)

    def put(self, request, session_id: int):
        self._check_perm(request, "edit_live_session")
        serializer = LiveSessionUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        result = services.update_live_session(
            session_id, serializer.validated_data, request.user
        )
        if result is None:
            return Response(
                {"detail": "Live session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if isinstance(result, str):
            return _string_to_response(result)
        return Response(LiveSessionSerializer(result).data)

    def delete(self, request, session_id: int):
        self._check_perm(request, "delete_live_session")
        result = services.delete_live_session(session_id, request.user)
        if result is None:
            return Response(
                {"detail": "Live session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if isinstance(result, str):
            return _string_to_response(result)
        return Response(LiveSessionSerializer(result).data)


class LiveSessionStatusView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("edit_live_session"),
    ]

    def patch(self, request, session_id: int):
        serializer = LiveSessionStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.update_live_session_status(
            session_id, serializer.validated_data["status"], request.user
        )
        if result is None:
            return Response(
                {"detail": "Live session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if isinstance(result, str):
            return _string_to_response(result)
        return Response(LiveSessionSerializer(result).data)


class LiveSessionRescheduleView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("edit_live_session"),
    ]

    def post(self, request, session_id: int):
        serializer = LiveSessionRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.reschedule_live_session(
            session_id, serializer.validated_data, request.user
        )
        if result is None:
            return Response(
                {"detail": "Live session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if isinstance(result, str):
            return _string_to_response(result)
        return Response(
            LiveSessionSerializer(result).data, status=status.HTTP_201_CREATED
        )


class LiveSessionAttendanceView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("view_live_session_detail"),
    ]

    def get(self, request, session_id: int):
        summary = services.get_attendance_summary(session_id)
        if summary is None:
            return Response(
                {"detail": "Live session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(summary)


class LiveSessionJoinView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("view_live_session_detail"),
    ]

    def post(self, request, session_id: int):
        session = services.get_live_session(session_id)
        if not session:
            return Response(
                {"detail": "Live session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if session.status == LiveSessionStatus.ENDED:
            return Response(
                {"detail": "Cette session est terminée."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not dj_settings.JITSI_APP_ID:
            return Response(
                {
                    "detail": (
                        "La visioconférence n'est pas configurée. "
                        "Veuillez définir JITSI_APP_ID."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        services.record_join(session, request.user)
        room = session.meeting_room_name or f"live-session-{session.id}"
        domain = dj_settings.JITSI_DOMAIN
        return Response(
            {
                "app_id": dj_settings.JITSI_APP_ID,
                "domain": domain,
                "room": room,
                "url": f"https://{domain}/{dj_settings.JITSI_APP_ID}/{room}",
                "jwt": dj_settings.JITSI_JWT or None,
                "uid": request.user.id,
            }
        )


class LiveSessionLeaveView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("view_live_session_detail"),
    ]

    def post(self, request, session_id: int):
        if not services.get_live_session(session_id):
            return Response(
                {"detail": "Live session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        services.record_leave(session_id, request.user)
        return Response({"detail": "Presence updated"})
