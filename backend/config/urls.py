from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.enrollments.views import CertificateDetailView
from apps.accounts.views_contact import ContactView


class RootView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return Response(
            {"message": f"Welcome to {settings.PROJECT_NAME} - Version {settings.PROJECT_VERSION}"}
        )


api_v1_patterns = [
    path("auth/", include("apps.accounts.urls_auth")),
    path("users/", include("apps.accounts.urls_users")),
    path("permissions/", include("apps.permissions.urls")),
    # Enrollment / progression / certificates routes are mounted UNDER
    # /api/v1/courses/ but resolved BEFORE the courses router so explicit
    # paths like /courses/<id>/enroll take precedence.
    path("courses/", include("apps.enrollments.urls")),
    # Top-level alias /api/v1/certificates/<id> -> CertificateDetailView
    # (front [course.ts -> getCertificateDetails] expects this short path).
    path(
        "certificates/<int:certificate_id>",
        CertificateDetailView.as_view(),
        name="certificate-detail-toplevel",
    ),
    path("", include("apps.courses.urls")),
    path("contents/", include("apps.content.urls")),
    path("payments/", include("apps.payments.urls")),
    path("live-sessions/", include("apps.live_sessions.urls")),
    path("student/", include("apps.student_dashboard.urls")),
    path("professors/", include("apps.professors.urls_professors")),
    path("admin/dashboard/", include("apps.professors.urls_admin_dashboard")),
    path("uploads/", include("apps.uploads.urls")),
    path("contact", ContactView.as_view(), name="contact"),
]

urlpatterns = [
    path("", RootView.as_view()),
    path("admin/", admin.site.urls),
    path(f"{settings.API_V1_PREFIX}/", include(api_v1_patterns)),
    # OpenAPI schema + Swagger / Redoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
