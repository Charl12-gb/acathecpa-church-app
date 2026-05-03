"""URLs mounted under /api/v1/professors/."""
from django.urls import path

from .views import (
    AddProfileView,
    CreateProfessorView,
    ProfessorDetailView,
    ProfessorProfilePermissionView,
    ProfDashboardStatsView,
    ProfPublishedCoursesView,
    ProfRecentActivitiesView,
    ProfStudentDistributionView,
    ProfStudentEngagementView,
    UpdateProfileView,
)


urlpatterns = [
    # Create professor user + profile
    path("", CreateProfessorView.as_view(), name="professors-create"),

    # Professor dashboard (mounted at /api/v1/professors/dashboard/...)
    path("dashboard/stats", ProfDashboardStatsView.as_view(), name="prof-dashboard-stats"),
    path(
        "dashboard/published-courses",
        ProfPublishedCoursesView.as_view(),
        name="prof-dashboard-published-courses",
    ),
    path(
        "dashboard/student-engagement",
        ProfStudentEngagementView.as_view(),
        name="prof-dashboard-student-engagement",
    ),
    path(
        "dashboard/student-distribution",
        ProfStudentDistributionView.as_view(),
        name="prof-dashboard-student-distribution",
    ),
    path(
        "dashboard/recent-activities",
        ProfRecentActivitiesView.as_view(),
        name="prof-dashboard-recent-activities",
    ),

    # Per-user profile routes
    path("<int:user_id>/profile", AddProfileView.as_view(), name="prof-profile-add"),
    path(
        "<int:user_id>/profile/update",
        UpdateProfileView.as_view(),
        name="prof-profile-update",
    ),
    path(
        "<int:user_id>/professor-profile",
        ProfessorProfilePermissionView.as_view(),
        name="prof-profile-permission",
    ),
    path("<int:user_id>", ProfessorDetailView.as_view(), name="professors-detail"),
]
