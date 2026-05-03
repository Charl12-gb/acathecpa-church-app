from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    CourseLessonViewSet,
    CourseSectionViewSet,
    CourseTestViewSet,
    CourseViewSet,
    TestQuestionViewSet,
)

# Use SimpleRouter (no API root view) and `trailing_slash="/?"` so both
# `/courses/` and `/courses` work — matches what the front-end already sends.
nested_router = SimpleRouter(trailing_slash="/?")
nested_router.register("sections", CourseSectionViewSet, basename="course-section")
nested_router.register("lessons", CourseLessonViewSet, basename="course-lesson")
nested_router.register("tests", CourseTestViewSet, basename="course-test")
nested_router.register("questions", TestQuestionViewSet, basename="test-question")

courses_router = SimpleRouter(trailing_slash="/?")
courses_router.register("courses", CourseViewSet, basename="course")

# IMPORTANT: list nested router FIRST so /courses/sections/... is matched before
# the CourseViewSet detail route /courses/<pk> would swallow it.
urlpatterns = [
    path("courses/", include(nested_router.urls)),
] + courses_router.urls
