from django.urls import path

from .views import (
    LiveSessionAttendanceView,
    LiveSessionDetailView,
    LiveSessionJoinView,
    LiveSessionLeaveView,
    LiveSessionListCreateView,
    LiveSessionRescheduleView,
    LiveSessionStatusView,
    LiveSessionsForCourseView,
)

urlpatterns = [
    path("", LiveSessionListCreateView.as_view(), name="live-sessions-list-create"),
    path(
        "course/<int:course_id>",
        LiveSessionsForCourseView.as_view(),
        name="live-sessions-for-course",
    ),
    path("<int:session_id>", LiveSessionDetailView.as_view(), name="live-session-detail"),
    path(
        "<int:session_id>/status",
        LiveSessionStatusView.as_view(),
        name="live-session-status",
    ),
    path(
        "<int:session_id>/reschedule",
        LiveSessionRescheduleView.as_view(),
        name="live-session-reschedule",
    ),
    path(
        "<int:session_id>/attendance",
        LiveSessionAttendanceView.as_view(),
        name="live-session-attendance",
    ),
    path("<int:session_id>/join", LiveSessionJoinView.as_view(), name="live-session-join"),
    path("<int:session_id>/leave", LiveSessionLeaveView.as_view(), name="live-session-leave"),
]
