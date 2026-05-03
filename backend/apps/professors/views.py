"""
Endpoints exposed by the `professors` app.

3 URL groups :
    - /api/v1/professors/                -> profile CRUD + creation flow
    - /api/v1/professors/dashboard/...   -> professor dashboard
    - /api/v1/admin/dashboard/...        -> admin dashboard
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import UserSerializer
from apps.permissions.permissions import HasPermission

from . import services
from .serializers import (
    AdminDashboardStatsSerializer,
    CoursePerformanceSerializer,
    MonthlyRegistrationSerializer,
    ProfessorDashboardStatsSerializer,
    ProfessorProfileCreateForExistingUserSerializer,
    ProfessorProfileSerializer,
    ProfessorProfileUpdateSerializer,
    ProfessorRecentActivitySerializer,
    ProfessorStatsSerializer,
    ProfessorUserAndProfileCreateSerializer,
    RecentActivitySerializer,
    StudentDistributionInProfessorCoursesSerializer,
    StudentEngagementSerializer,
    UserDistributionSerializer,
)

MANAGE_PROFESSOR_PROFILES = "manage_professor_profiles"
VIEW_ANY_USER_PROFILE_DETAIL = "view_any_user_profile_detail"


# --------------------------------------------------------------------------- #
# Custom role-based permissions (mirror FastAPI `require_admin` / `require_professor`)
# --------------------------------------------------------------------------- #
class IsAdmin(BasePermission):
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        role = getattr(user, "role", None)
        return bool(role and role.name in {"admin", "super_admin"})


class IsProfessor(BasePermission):
    message = "Accès réservé aux professeurs."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        role = getattr(user, "role", None)
        return bool(role and role.name in {"professor", "admin", "super_admin"})


# --------------------------------------------------------------------------- #
# Profile endpoints
# --------------------------------------------------------------------------- #
class CreateProfessorView(APIView):
    """`POST /api/v1/professors/` — create both the user and the profile."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = ProfessorUserAndProfileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.create_professor_user_and_profile(serializer.validated_data)
        if result == "EmailAlreadyExists":
            return Response(
                {"detail": "Un utilisateur avec cet email existe déjà."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if result == "ProfessorRoleMissing":
            return Response(
                {"detail": "Le rôle 'professor' est introuvable. Lance `seed_permissions`."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(UserSerializer(result).data, status=status.HTTP_201_CREATED)


class AddProfileView(APIView):
    """`POST /api/v1/professors/<user_id>/profile`"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id: int):
        serializer = ProfessorProfileCreateForExistingUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = services.add_profile_to_existing_user(user_id, serializer.validated_data)
        if result == "UserNotFound":
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if result == "ProfileAlreadyExists":
            return Response(
                {"detail": "Professor profile already exists for this user."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            ProfessorProfileSerializer(result).data, status=status.HTTP_201_CREATED
        )

    def put(self, request, user_id: int):
        serializer = ProfessorProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = services.update_profile(user_id, serializer.validated_data)
        if not profile:
            return Response(
                {
                    "detail": "Profil de professeur non trouvé pour cet utilisateur, "
                    "mise à jour impossible."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProfessorProfileSerializer(profile).data)

    def delete(self, request, user_id: int):
        profile = services.delete_profile(user_id)
        if not profile:
            return Response(
                {"detail": "Professor profile not found for this user, cannot delete."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProfessorProfileSerializer(profile).data)


class UpdateProfileView(APIView):
    """Legacy alias kept for backward-compat: PUT /professors/<id>/profile/update."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, user_id: int):
        serializer = ProfessorProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = services.update_profile(user_id, serializer.validated_data)
        if not profile:
            return Response(
                {
                    "detail": "Profil de professeur non trouvé pour cet utilisateur, "
                    "mise à jour impossible."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProfessorProfileSerializer(profile).data)


class ProfessorDetailView(APIView):
    """`GET /api/v1/professors/<user_id>` — User + profile."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, user_id: int):
        from apps.accounts.models import User
        user = (
            User.objects.filter(pk=user_id)
            .select_related("role", "professor_profile")
            .first()
        )
        if not user:
            return Response(
                {"detail": "Professeur (Utilisateur) non trouvé."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(UserSerializer(user).data)


class ProfessorProfilePermissionView(APIView):
    """
    Same as the previous ones but gated by explicit permissions
    (mirrors the duplicate `/{user_id}/professor-profile` routes in FastAPI).

    GET    -> requires `view_any_user_profile_detail`
    PUT    -> requires `manage_professor_profiles`
    DELETE -> requires `manage_professor_profiles`
    """
    permission_classes = [IsAuthenticated]

    def _check_perm(self, request, perm: str):
        if not HasPermission.with_name(perm)().has_permission(request, self):
            self.permission_denied(request)

    def get(self, request, user_id: int):
        self._check_perm(request, VIEW_ANY_USER_PROFILE_DETAIL)
        profile = services.get_profile_by_user_id(user_id)
        if not profile:
            return Response(
                {"detail": "Professor profile not found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProfessorProfileSerializer(profile).data)

    def put(self, request, user_id: int):
        self._check_perm(request, MANAGE_PROFESSOR_PROFILES)
        serializer = ProfessorProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = services.update_profile(user_id, serializer.validated_data)
        if not profile:
            return Response(
                {"detail": "Professor profile not found for this user, cannot update."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProfessorProfileSerializer(profile).data)

    def delete(self, request, user_id: int):
        self._check_perm(request, MANAGE_PROFESSOR_PROFILES)
        profile = services.delete_profile(user_id)
        if not profile:
            return Response(
                {"detail": "Professor profile not found for this user, cannot delete."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProfessorProfileSerializer(profile).data)


# --------------------------------------------------------------------------- #
# Admin dashboard endpoints
# --------------------------------------------------------------------------- #
class _BaseAdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]


class AdminStatsView(_BaseAdminDashboardView):
    def get(self, request):
        return Response(
            AdminDashboardStatsSerializer(services.get_admin_dashboard_stats()).data
        )


class AdminProfessorsView(_BaseAdminDashboardView):
    def get(self, request):
        return Response(
            ProfessorStatsSerializer(services.get_admin_professors(), many=True).data
        )


class AdminProfessorCoursesView(_BaseAdminDashboardView):
    def get(self, request, professor_id: int):
        from apps.courses.serializers import CourseListSerializer
        skip = int(request.query_params.get("skip", 0))
        limit = int(request.query_params.get("limit", 100))
        courses = services.get_courses_for_professor_admin(professor_id, skip, limit)
        return Response(CourseListSerializer(courses, many=True).data)


class AdminRecentActivitiesView(_BaseAdminDashboardView):
    def get(self, request):
        return Response(
            RecentActivitySerializer(services.get_admin_recent_activities(), many=True).data
        )


class AdminUserDistributionView(_BaseAdminDashboardView):
    def get(self, request):
        return Response(
            UserDistributionSerializer(services.get_admin_user_distribution()).data
        )


class AdminMonthlyRegistrationsView(_BaseAdminDashboardView):
    def get(self, request):
        return Response(
            MonthlyRegistrationSerializer(
                services.get_admin_monthly_registrations(), many=True
            ).data
        )


# --------------------------------------------------------------------------- #
# Professor dashboard endpoints
# --------------------------------------------------------------------------- #
class _BaseProfessorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsProfessor]


class ProfDashboardStatsView(_BaseProfessorDashboardView):
    def get(self, request):
        return Response(
            ProfessorDashboardStatsSerializer(
                services.get_professor_dashboard_stats(request.user)
            ).data
        )


class ProfPublishedCoursesView(_BaseProfessorDashboardView):
    def get(self, request):
        return Response(
            CoursePerformanceSerializer(
                services.get_professor_published_courses(request.user), many=True
            ).data
        )


class ProfStudentEngagementView(_BaseProfessorDashboardView):
    def get(self, request):
        return Response(
            StudentEngagementSerializer(
                services.get_professor_student_engagement(request.user), many=True
            ).data
        )


class ProfStudentDistributionView(_BaseProfessorDashboardView):
    def get(self, request):
        return Response(
            StudentDistributionInProfessorCoursesSerializer(
                services.get_professor_student_distribution(request.user)
            ).data
        )


class ProfRecentActivitiesView(_BaseProfessorDashboardView):
    def get(self, request):
        return Response(
            ProfessorRecentActivitySerializer(
                services.get_professor_recent_activities(request.user), many=True
            ).data
        )
