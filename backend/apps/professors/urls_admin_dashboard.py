"""URLs mounted under /api/v1/admin/dashboard/."""
from django.urls import path

from .views import (
    AdminMonthlyRegistrationsView,
    AdminProfessorCoursesView,
    AdminProfessorsView,
    AdminRecentActivitiesView,
    AdminStatsView,
    AdminUserDistributionView,
)


urlpatterns = [
    path("stats", AdminStatsView.as_view(), name="admin-dashboard-stats"),
    path("professors", AdminProfessorsView.as_view(), name="admin-dashboard-professors"),
    path(
        "professors/<int:professor_id>/courses",
        AdminProfessorCoursesView.as_view(),
        name="admin-dashboard-professor-courses",
    ),
    path(
        "recent-activities",
        AdminRecentActivitiesView.as_view(),
        name="admin-dashboard-recent-activities",
    ),
    path(
        "user-distribution",
        AdminUserDistributionView.as_view(),
        name="admin-dashboard-user-distribution",
    ),
    path(
        "monthly-registrations",
        AdminMonthlyRegistrationsView.as_view(),
        name="admin-dashboard-monthly-registrations",
    ),
]
