"""
URLs for enrollments + progression + certificates.

These are mounted under `/api/v1/courses/` to match the FastAPI router prefix.
"""
from django.urls import path

from .views import (
    CertificateDetailView,
    CheckAndIssueCertificateView,
    EnrollView,
    IssueUserCourseCertificateView,
    MarkLessonCompletedView,
    MarkSectionCompletedView,
    MyCertificatesView,
    MyCourseCertificateView,
    MyCourseProgressView,
    MyEnrolledCoursesView,
    SubmitTestAttemptView,
    UnenrollView,
    UserCertificatesView,
)

urlpatterns = [
    # Enrollment
    path("<int:course_id>/enroll", EnrollView.as_view(), name="course-enroll"),
    path("<int:course_id>/unenroll", UnenrollView.as_view(), name="course-unenroll"),
    path("me/enrolled", MyEnrolledCoursesView.as_view(), name="my-enrolled-courses"),
    # Progression
    path(
        "<int:course_id>/me/progress",
        MyCourseProgressView.as_view(),
        name="my-course-progress",
    ),
    path(
        "<int:course_id>/lessons/<int:lesson_id>/complete",
        MarkLessonCompletedView.as_view(),
        name="mark-lesson-completed",
    ),
    path(
        "<int:course_id>/sections/<int:section_id>/complete",
        MarkSectionCompletedView.as_view(),
        name="mark-section-completed",
    ),
    path(
        "<int:course_id>/tests/<int:test_id>/attempt",
        SubmitTestAttemptView.as_view(),
        name="submit-test-attempt",
    ),
    # Certificates
    path(
        "<int:course_id>/me/check-certificate",
        CheckAndIssueCertificateView.as_view(),
        name="check-and-issue-certificate",
    ),
    path(
        "<int:course_id>/certificate",
        MyCourseCertificateView.as_view(),
        name="my-course-certificate",
    ),
    path("me/certificates", MyCertificatesView.as_view(), name="my-certificates"),
    path(
        "<int:course_id>/users/<int:user_id>/certificates/",
        IssueUserCourseCertificateView.as_view(),
        name="issue-user-course-certificate",
    ),
    path(
        "users/<int:user_id>/certificates/",
        UserCertificatesView.as_view(),
        name="user-certificates",
    ),
    path(
        "certificates/<int:certificate_id>",
        CertificateDetailView.as_view(),
        name="certificate-detail",
    ),
]
