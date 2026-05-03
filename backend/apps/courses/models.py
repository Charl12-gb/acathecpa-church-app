"""
Course-related models.

Mirrors `backend/app/models/course.py`, `course_section.py`, `course_lesson.py`,
`course_test.py` and `test_question.py` from the FastAPI backend.
"""
from django.conf import settings
from django.db import models


# --------------------------------------------------------------------------- #
# Enums (TextChoices)
# --------------------------------------------------------------------------- #
class CourseStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class CourseSectionType(models.TextChoices):
    TEXT = "text", "Text"
    VIDEO = "video", "Video"
    QUIZ = "quiz", "Quiz"


class LessonType(models.TextChoices):
    VIDEO = "video", "Video"
    TEXT = "text", "Text"
    QUIZ = "quiz", "Quiz"


class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = "multiple_choice", "Multiple choice"


# --------------------------------------------------------------------------- #
# Course
# --------------------------------------------------------------------------- #
class Course(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=512, blank=True, null=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructed_courses",
        db_column="instructor_id",
    )
    status = models.CharField(
        max_length=16, choices=CourseStatus.choices, default=CourseStatus.DRAFT
    )
    price = models.FloatField(blank=True, null=True, default=0.0)
    is_free = models.BooleanField(default=False)
    objectives = models.JSONField(blank=True, null=True)
    prerequisites = models.JSONField(blank=True, null=True)
    points_required_for_certificate = models.IntegerField(blank=True, null=True)
    category = models.CharField(max_length=128, blank=True, null=True)
    level = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} (#{self.pk})"


# --------------------------------------------------------------------------- #
# Section
# --------------------------------------------------------------------------- #
class CourseSection(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="sections", db_column="course_id"
    )
    title = models.CharField(max_length=255, db_index=True)
    order = models.IntegerField()
    content_type = models.CharField(
        max_length=16, choices=CourseSectionType.choices, default=CourseSectionType.TEXT
    )
    video_url = models.CharField(max_length=512, blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "course_sections"
        ordering = ["course_id", "order"]


# --------------------------------------------------------------------------- #
# Lesson
# --------------------------------------------------------------------------- #
class CourseLesson(models.Model):
    section = models.ForeignKey(
        CourseSection,
        on_delete=models.CASCADE,
        related_name="lessons",
        db_column="section_id",
    )
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=16, choices=LessonType.choices)
    content_body = models.TextField(blank=True, null=True)
    video_url = models.CharField(max_length=512, blank=True, null=True)
    duration = models.CharField(max_length=64, blank=True, null=True)
    order = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_lessons"
        ordering = ["section_id", "order"]


# --------------------------------------------------------------------------- #
# Test (per section)
# --------------------------------------------------------------------------- #
class CourseTest(models.Model):
    section = models.OneToOneField(
        CourseSection,
        on_delete=models.CASCADE,
        related_name="test",
        null=True,
        blank=True,
        db_column="section_id",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(blank=True, null=True)
    passing_score = models.IntegerField(blank=True, null=True)
    max_attempts = models.IntegerField(blank=True, null=True, default=1)

    class Meta:
        db_table = "course_tests"


# --------------------------------------------------------------------------- #
# Test question
# --------------------------------------------------------------------------- #
class TestQuestion(models.Model):
    test = models.ForeignKey(
        CourseTest,
        on_delete=models.CASCADE,
        related_name="questions",
        db_column="test_id",
    )
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=32, choices=QuestionType.choices, default=QuestionType.MULTIPLE_CHOICE
    )
    options = models.JSONField(blank=True, null=True)
    correct_answer_data = models.JSONField(blank=True, null=True)
    points = models.IntegerField(default=1)

    class Meta:
        db_table = "test_questions"
