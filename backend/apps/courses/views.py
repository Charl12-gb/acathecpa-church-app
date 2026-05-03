"""
Course-related ViewSets.

Endpoint mapping (≈ FastAPI `course_router`):

    POST   /api/v1/courses/                                  create_course
    GET    /api/v1/courses/                                  view_any_course_listing
    GET    /api/v1/courses/{id}/                             view_course_detail
    PUT    /api/v1/courses/{id}/                             edit_own_course
    PATCH  /api/v1/courses/{id}/                             edit_own_course
    DELETE /api/v1/courses/{id}/                             delete_own_course
    POST   /api/v1/courses/{id}/publish/                     publish_course
    GET    /api/v1/courses/instructor/me/                    view_own_instructed_courses

    GET/POST  /api/v1/courses/{course_id}/sections/          create_course_section / view_course_sections
    GET/PUT/PATCH/DELETE /api/v1/sections/{id}/              view_course_section_detail / edit_course_section / delete_course_section

    GET/POST  /api/v1/sections/{section_id}/lessons/         create_course_lesson / view_course_lessons
    GET/PUT/PATCH/DELETE /api/v1/lessons/{id}/               view_course_lesson_detail / edit_course_lesson / delete_course_lesson

    POST   /api/v1/sections/{section_id}/tests/              create_course_test
    GET    /api/v1/sections/{section_id}/tests/              view_course_test
    GET/PUT/PATCH/DELETE /api/v1/tests/{id}/                 view_course_test / edit_course_test / delete_course_test

    GET/POST  /api/v1/tests/{test_id}/questions/             create_test_question / view_test_questions
    GET/PUT/PATCH/DELETE /api/v1/questions/{id}/             view_test_questions / edit_test_question / delete_test_question
"""
from __future__ import annotations

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.permissions.permissions import HasPermission

from . import permissions_helpers as perm_helpers


def _require(request, view, permission_name: str) -> None:
    """Raise PermissionDenied if `request.user` lacks `permission_name`."""
    if not HasPermission.with_name(permission_name)().has_permission(request, view):
        view.permission_denied(request, message=f"Requires permission: {permission_name}")


from .models import (
    Course,
    CourseLesson,
    CourseSection,
    CourseStatus,
    CourseTest,
    TestQuestion,
)
from .serializers import (
    CourseDetailSerializer,
    CourseLessonSerializer,
    CourseListSerializer,
    CourseSectionSerializer,
    CourseSectionWriteSerializer,
    CourseTestSerializer,
    CourseWriteSerializer,
    TestQuestionSerializer,
    TestQuestionWriteSerializer,
)


# --------------------------------------------------------------------------- #
# Courses
# --------------------------------------------------------------------------- #
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("instructor", "instructor__role").all()

    permission_map = {
        "list": "view_any_course_listing",
        "create": "create_course",
        "retrieve": "view_course_detail",
        "update": "edit_own_course",
        "partial_update": "edit_own_course",
        "destroy": "delete_own_course",
        "publish": "publish_course",
        "instructor_me": "view_own_instructed_courses",
        "my_enrolled": "view_own_enrolled_courses",
        "list_sections": "view_course_sections",
        "create_section": "create_course_section",
    }

    filterset_fields = ["status", "category", "level", "is_free"]
    search_fields = ["title", "description", "category"]
    ordering_fields = ["created_at", "updated_at", "title", "price"]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        if self.action == "retrieve":
            return CourseDetailSerializer
        if self.action in {"create", "update", "partial_update"}:
            return CourseWriteSerializer
        return CourseDetailSerializer

    def get_permissions(self):
        # Public read access for list/retrieve (catalog browsing).
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
            status_filter = self.request.query_params.get("status", CourseStatus.PUBLISHED)
            if status_filter:
                qs = qs.filter(status=status_filter)
        return qs

    # --- Custom create / update / destroy with ownership semantics ---
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    def update(self, request, *args, **kwargs):
        course = self.get_object()
        perm_helpers.assert_can_edit_course(request.user, course)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        perm_helpers.assert_can_edit_course(request.user, course)
        return super().destroy(request, *args, **kwargs)

    # --- Custom actions ---
    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        course = self.get_object()
        perm_helpers.assert_can_edit_course(request.user, course)
        course.status = CourseStatus.PUBLISHED
        course.save(update_fields=["status", "updated_at"])
        return Response(CourseDetailSerializer(course).data)

    @action(detail=False, methods=["get"], url_path="instructor/me")
    def instructor_me(self, request):
        qs = self.get_queryset().filter(instructor=request.user)
        page = self.paginate_queryset(qs)
        serializer = CourseListSerializer(page or qs, many=True)
        return self.get_paginated_response(serializer.data) if page is not None else Response(serializer.data)

    # --- Nested: sections of a course ---
    @action(detail=True, methods=["get", "post"], url_path="sections")
    def sections(self, request, pk=None):
        course = self.get_object()
        if request.method == "GET":
            self.action = "list_sections"
            self.check_permissions(request)
            qs = course.sections.all()
            return Response(CourseSectionSerializer(qs, many=True).data)

        # POST -> create section
        self.action = "create_section"
        self.check_permissions(request)
        perm_helpers.assert_can_edit_course(request.user, course)
        serializer = CourseSectionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        section = serializer.save(course=course)
        return Response(
            CourseSectionSerializer(section).data, status=status.HTTP_201_CREATED
        )


# --------------------------------------------------------------------------- #
# Sections — detail / update / delete
# --------------------------------------------------------------------------- #
class CourseSectionViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = CourseSection.objects.select_related("course", "test").prefetch_related("lessons")

    permission_map = {
        "retrieve": "view_course_section_detail",
        "update": "edit_course_section",
        "partial_update": "edit_course_section",
        "destroy": "delete_course_section",
        "lessons": None,  # GET: view_course_lessons / POST: create_course_lesson
    }

    def get_serializer_class(self):
        if self.action in {"update", "partial_update"}:
            return CourseSectionWriteSerializer
        return CourseSectionSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        perm_name = self.permission_map.get(self.action)
        if perm_name:
            permission_classes.append(HasPermission.with_name(perm_name))
        return [p() for p in permission_classes]

    def update(self, request, *args, **kwargs):
        perm_helpers.assert_can_edit_section(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        perm_helpers.assert_can_edit_section(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)

    # --- Nested: lessons of a section ---
    @action(detail=True, methods=["get", "post"], url_path="lessons")
    def lessons(self, request, pk=None):
        section = self.get_object()
        if request.method == "GET":
            _require(request, self, "view_course_lessons")
            qs = section.lessons.all()
            return Response(CourseLessonSerializer(qs, many=True).data)

        # POST -> create lesson
        _require(request, self, "create_course_lesson")
        perm_helpers.assert_can_edit_section(request.user, section)
        serializer = CourseLessonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save(section=section)
        return Response(CourseLessonSerializer(lesson).data, status=status.HTTP_201_CREATED)

    # --- Nested: test of a section ---
    @action(detail=True, methods=["get", "post"], url_path="tests")
    def test(self, request, pk=None):
        section = self.get_object()
        if request.method == "GET":
            _require(request, self, "view_course_test")
            test_obj = getattr(section, "test", None)
            if not test_obj:
                return Response({}, status=status.HTTP_200_OK)
            return Response(CourseTestSerializer(test_obj).data)

        _require(request, self, "create_course_test")
        perm_helpers.assert_can_edit_section(request.user, section)
        serializer = CourseTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        test_obj = serializer.save(section=section)
        return Response(CourseTestSerializer(test_obj).data, status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------- #
# Lessons
# --------------------------------------------------------------------------- #
class CourseLessonViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = CourseLesson.objects.select_related("section", "section__course").all()
    serializer_class = CourseLessonSerializer

    permission_map = {
        "retrieve": "view_course_lesson_detail",
        "update": "edit_course_lesson",
        "partial_update": "edit_course_lesson",
        "destroy": "delete_course_lesson",
    }

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        perm_name = self.permission_map.get(self.action)
        if perm_name:
            permission_classes.append(HasPermission.with_name(perm_name))
        return [p() for p in permission_classes]

    def update(self, request, *args, **kwargs):
        perm_helpers.assert_can_edit_lesson(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        perm_helpers.assert_can_edit_lesson(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
class CourseTestViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = CourseTest.objects.select_related("section", "section__course").prefetch_related("questions")
    serializer_class = CourseTestSerializer

    permission_map = {
        "retrieve": "view_course_test",
        "update": "edit_course_test",
        "partial_update": "edit_course_test",
        "destroy": "delete_course_test",
    }

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        perm_name = self.permission_map.get(self.action)
        if perm_name:
            permission_classes.append(HasPermission.with_name(perm_name))
        return [p() for p in permission_classes]

    def update(self, request, *args, **kwargs):
        perm_helpers.assert_can_edit_test(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        perm_helpers.assert_can_edit_test(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get", "post"], url_path="questions")
    def questions(self, request, pk=None):
        test_obj = self.get_object()
        if request.method == "GET":
            _require(request, self, "view_test_questions")
            return Response(TestQuestionSerializer(test_obj.questions.all(), many=True).data)

        _require(request, self, "create_test_question")
        perm_helpers.assert_can_edit_test(request.user, test_obj)
        serializer = TestQuestionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save(test=test_obj)
        return Response(TestQuestionSerializer(question).data, status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------- #
# Questions
# --------------------------------------------------------------------------- #
class TestQuestionViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = TestQuestion.objects.select_related("test", "test__section", "test__section__course").all()
    serializer_class = TestQuestionSerializer

    permission_map = {
        "retrieve": "view_test_questions",
        "update": "edit_test_question",
        "partial_update": "edit_test_question",
        "destroy": "delete_test_question",
    }

    def get_serializer_class(self):
        if self.action in {"update", "partial_update"}:
            return TestQuestionWriteSerializer
        return TestQuestionSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        perm_name = self.permission_map.get(self.action)
        if perm_name:
            permission_classes.append(HasPermission.with_name(perm_name))
        return [p() for p in permission_classes]

    def update(self, request, *args, **kwargs):
        perm_helpers.assert_can_edit_question(request.user, self.get_object())
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        perm_helpers.assert_can_edit_question(request.user, self.get_object())
        return super().destroy(request, *args, **kwargs)
