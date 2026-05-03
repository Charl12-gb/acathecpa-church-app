"""
Enrollment, progression and certificate endpoints.

Mirrors the FastAPI endpoints, mounted at:

    /api/v1/courses/{course_id}/enroll                  POST
    /api/v1/courses/{course_id}/unenroll                POST
    /api/v1/courses/me/enrolled                         GET
    /api/v1/courses/me/certificates                     GET
    /api/v1/courses/{course_id}/me/progress             GET
    /api/v1/courses/{course_id}/lessons/{lesson_id}/complete   POST
    /api/v1/courses/{course_id}/sections/{section_id}/complete POST
    /api/v1/courses/{course_id}/tests/{test_id}/attempt        POST
    /api/v1/courses/{course_id}/me/check-certificate    POST
    /api/v1/courses/{course_id}/certificate             GET
    /api/v1/courses/{course_id}/users/{user_id}/certificates/  POST  (issue)
    /api/v1/courses/users/{user_id}/certificates/       GET
    /api/v1/courses/certificates/{certificate_id}       GET
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models import Course
from apps.courses.serializers import CourseListSerializer
from apps.permissions.permissions import HasPermission

from . import services
from .serializers import (
    CertificateDisplaySerializer,
    CertificateSerializer,
    EnrollmentProgressSerializer,
    TestAttemptInputSerializer,
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _is_admin(user) -> bool:
    role = getattr(user, "role", None)
    return bool(role and role.name in ("admin", "super_admin"))


def _perm(name: str):
    return [IsAuthenticated, HasPermission.with_name(name)]


# --------------------------------------------------------------------------- #
# Enrollment
# --------------------------------------------------------------------------- #
class EnrollView(APIView):
    permission_classes = [IsAuthenticated, HasPermission.with_name("enroll_in_course")]

    def post(self, request, course_id: int):
        result = services.enroll_student_in_course(course_id, request.user.id)
        if isinstance(result, str):
            mapping = {
                "NotFound": (status.HTTP_404_NOT_FOUND, "Course or user not found."),
                "CourseNotPublished": (
                    status.HTTP_400_BAD_REQUEST,
                    "Course is not published.",
                ),
                "AlreadyEnrolled": (
                    status.HTTP_400_BAD_REQUEST,
                    "Already enrolled in this course.",
                ),
                "PaymentRequired": (
                    status.HTTP_402_PAYMENT_REQUIRED,
                    "Payment required for this course.",
                ),
            }
            code, message = mapping.get(
                result, (status.HTTP_400_BAD_REQUEST, result)
            )
            return Response({"detail": message}, status=code)

        return Response(
            {
                "detail": "Enrolled successfully.",
                "user_id": result.user_id,
                "course_id": result.course_id,
                "enrolled_at": result.enrolled_at,
            },
            status=status.HTTP_201_CREATED,
        )


class UnenrollView(APIView):
    permission_classes = [IsAuthenticated, HasPermission.with_name("unenroll_from_course")]

    def post(self, request, course_id: int):
        result = services.unenroll_student_from_course(course_id, request.user.id)
        if result == "NotEnrolled":
            return Response(
                {"detail": "Not enrolled in this course."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"detail": "Unenrolled successfully."})


class MyEnrolledCoursesView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("view_own_enrolled_courses"),
    ]

    def get(self, request):
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 100))
        courses = services.get_user_enrolled_courses(request.user.id, skip, limit)
        return Response(CourseListSerializer(courses, many=True).data)


# --------------------------------------------------------------------------- #
# Progression
# --------------------------------------------------------------------------- #
class MyCourseProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id: int):
        enrollment = services.get_enrollment(request.user.id, course_id)
        if not enrollment:
            return Response(
                {"detail": "Not enrolled in this course."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # Refresh derived fields
        services.auto_complete_sections(enrollment, course_id)
        enrollment.progress_percentage = services._calculate_progress_percentage(
            enrollment
        )
        enrollment.save(update_fields=["completed_sections", "progress_percentage"])
        return Response(EnrollmentProgressSerializer(enrollment).data)


class MarkLessonCompletedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id: int, lesson_id: int):
        enrollment = services.mark_lesson_completed(
            request.user.id, course_id, lesson_id
        )
        if not enrollment:
            return Response(
                {"detail": "Enrollment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(EnrollmentProgressSerializer(enrollment).data)


class MarkSectionCompletedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id: int, section_id: int):
        enrollment = services.mark_section_completed(
            request.user.id, course_id, section_id
        )
        if not enrollment:
            return Response(
                {"detail": "Enrollment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(EnrollmentProgressSerializer(enrollment).data)


class SubmitTestAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id: int, test_id: int):
        # Must be enrolled
        if not services.get_enrollment(request.user.id, course_id):
            raise PermissionDenied("User not enrolled in this course.")

        serializer = TestAttemptInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        enrollment = services.record_test_attempt(
            user_id=request.user.id,
            course_id=course_id,
            test_id=test_id,
            score=data["score"],
            passed=data["passed"],
            questions_summary=[dict(q) for q in data.get("questions_summary", [])],
        )
        if not enrollment:
            return Response(
                {"detail": "Failed to record test attempt."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(EnrollmentProgressSerializer(enrollment).data)


# --------------------------------------------------------------------------- #
# Certificates
# --------------------------------------------------------------------------- #
class CheckAndIssueCertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id: int):
        result = services.check_and_issue_certificate(request.user.id, course_id)
        if isinstance(result, str):
            mapping = {
                "EnrollmentNotFound": (
                    status.HTTP_404_NOT_FOUND,
                    "Vous n'êtes pas inscrit à ce cours.",
                ),
                "CourseNotFound": (
                    status.HTTP_404_NOT_FOUND,
                    "Cours introuvable.",
                ),
                "CertificateAlreadyIssued": (
                    status.HTTP_200_OK,
                    None,  # Return the existing cert below
                ),
                "NotAllLessonsCompleted": (
                    status.HTTP_400_BAD_REQUEST,
                    "Toutes les leçons n'ont pas été complétées.",
                ),
                "NotAllSectionsCompleted": (
                    status.HTTP_400_BAD_REQUEST,
                    "Toutes les sections n'ont pas été complétées.",
                ),
                "CertificateCreationError": (
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Erreur interne lors de la création du certificat.",
                ),
            }
            if result == "CertificateAlreadyIssued":
                cert = services.get_certificate_for_course_by_user(
                    request.user.id, course_id
                )
                return Response(
                    CertificateDisplaySerializer(cert).data if cert else None
                )
            if result.startswith("PointsNotMet"):
                _, ratio = result.split(":", 1)
                return Response(
                    {"detail": f"Points insuffisants : {ratio}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            code, msg = mapping.get(result, (status.HTTP_400_BAD_REQUEST, result))
            return Response({"detail": msg}, status=code)

        return Response(
            CertificateDisplaySerializer(result).data,
            status=status.HTTP_201_CREATED,
        )


class MyCourseCertificateView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("view_own_course_certificate"),
    ]

    def get(self, request, course_id: int):
        if not Course.objects.filter(pk=course_id).exists():
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        cert = services.get_certificate_for_course_by_user(request.user.id, course_id)
        if not cert:
            return Response(None)
        return Response(CertificateDisplaySerializer(cert).data)


class MyCertificatesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 100))
        certs = services.get_certificates_for_user(request.user.id, skip, limit)
        return Response(CertificateDisplaySerializer(certs, many=True).data)


class IssueUserCourseCertificateView(APIView):
    """Admin-style endpoint: explicitly issue a certificate to a user for a course."""

    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("issue_certificate"),
    ]

    def post(self, request, course_id: int, user_id: int):
        if not Course.objects.filter(pk=course_id).exists():
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        cert = services.create_certificate(user_id=user_id, course_id=course_id)
        if not cert:
            return Response(
                {"detail": "Could not create certificate."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            CertificateSerializer(cert).data, status=status.HTTP_201_CREATED
        )


class UserCertificatesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id: int):
        # Either viewing own certificates, or being admin
        if request.user.id != user_id and not _is_admin(request.user):
            raise PermissionDenied("Not authorized to view these certificates.")
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 100))
        certs = services.get_certificates_for_user(user_id, skip, limit)
        return Response(CertificateDisplaySerializer(certs, many=True).data)


class CertificateDetailView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasPermission.with_name("view_certificate_detail"),
    ]

    def get(self, request, certificate_id: int):
        cert = services.get_certificate_by_id(certificate_id)
        if not cert:
            return Response(
                {"detail": "Certificate not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(CertificateSerializer(cert).data)
