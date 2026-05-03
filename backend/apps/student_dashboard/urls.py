from django.urls import path

from .views import (
    EnrolledCoursesView,
    OverallProgressView,
    RecentCertificatesView,
    RecommendedCoursesView,
    StatsView,
    WeeklyActivityView,
)

urlpatterns = [
    path("dashboard/stats", StatsView.as_view(), name="student-dashboard-stats"),
    path(
        "dashboard/enrolled-courses",
        EnrolledCoursesView.as_view(),
        name="student-dashboard-enrolled-courses",
    ),
    path(
        "dashboard/overall-progress",
        OverallProgressView.as_view(),
        name="student-dashboard-overall-progress",
    ),
    path(
        "dashboard/weekly-activity",
        WeeklyActivityView.as_view(),
        name="student-dashboard-weekly-activity",
    ),
    path(
        "dashboard/recommended-courses",
        RecommendedCoursesView.as_view(),
        name="student-dashboard-recommended-courses",
    ),
    path(
        "dashboard/recent-certificates",
        RecentCertificatesView.as_view(),
        name="student-dashboard-recent-certificates",
    ),
]
