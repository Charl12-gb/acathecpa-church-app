from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Course, CourseLesson, CourseSection, CourseTest, TestQuestion


# --------------------------------------------------------------------------- #
# Question
# --------------------------------------------------------------------------- #
class QuestionOptionSerializer(serializers.Serializer):
    """Used as a hint for `options` JSON content (not enforced by the DB)."""
    text = serializers.CharField()
    is_correct = serializers.BooleanField()


class TestQuestionSerializer(serializers.ModelSerializer):
    test_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = TestQuestion
        fields = (
            "id", "test", "test_id", "question_text", "question_type",
            "options", "correct_answer_data", "points",
        )
        read_only_fields = ("id", "test", "test_id")


class TestQuestionWriteSerializer(serializers.ModelSerializer):
    """Used when creating/updating a question via /tests/<test_id>/questions/."""
    class Meta:
        model = TestQuestion
        fields = (
            "id", "question_text", "question_type",
            "options", "correct_answer_data", "points",
        )
        read_only_fields = ("id",)


# --------------------------------------------------------------------------- #
# Test
# --------------------------------------------------------------------------- #
class CourseTestSerializer(serializers.ModelSerializer):
    questions = TestQuestionWriteSerializer(many=True, required=False)
    section_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = CourseTest
        fields = (
            "id", "section", "section_id", "title", "description",
            "duration_minutes", "passing_score", "max_attempts",
            "questions",
        )
        read_only_fields = ("id", "section", "section_id")

    def create(self, validated_data: dict) -> CourseTest:
        questions = validated_data.pop("questions", [])
        test = CourseTest.objects.create(**validated_data)
        for q in questions:
            TestQuestion.objects.create(test=test, **q)
        return test

    def update(self, instance: CourseTest, validated_data: dict) -> CourseTest:
        questions = validated_data.pop("questions", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions is not None:
            # Replace strategy (mirrors FastAPI behaviour where questions list is sent again)
            instance.questions.all().delete()
            for q in questions:
                TestQuestion.objects.create(test=instance, **q)
        return instance


# --------------------------------------------------------------------------- #
# Lesson
# --------------------------------------------------------------------------- #
class CourseLessonSerializer(serializers.ModelSerializer):
    section_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CourseLesson
        fields = (
            "id", "section", "section_id", "title", "type", "content_body",
            "video_url", "duration", "order", "is_completed",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "section", "section_id", "created_at", "updated_at")


# --------------------------------------------------------------------------- #
# Section
# --------------------------------------------------------------------------- #
class CourseSectionSerializer(serializers.ModelSerializer):
    lessons = CourseLessonSerializer(many=True, read_only=True)
    test = CourseTestSerializer(read_only=True)
    course_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CourseSection
        fields = (
            "id", "course", "course_id", "title", "order",
            "content_type", "video_url", "text_content",
            "lessons", "test",
        )
        read_only_fields = ("id", "course", "course_id", "lessons", "test")


class CourseSectionWriteSerializer(serializers.ModelSerializer):
    """Allows creating a section together with an optional embedded test."""
    test = CourseTestSerializer(required=False, allow_null=True)

    class Meta:
        model = CourseSection
        fields = (
            "id", "title", "order",
            "content_type", "video_url", "text_content",
            "test",
        )
        read_only_fields = ("id",)

    def create(self, validated_data: dict) -> CourseSection:
        test_data = validated_data.pop("test", None)
        section = CourseSection.objects.create(**validated_data)
        if test_data:
            questions = test_data.pop("questions", [])
            test = CourseTest.objects.create(section=section, **test_data)
            for q in questions:
                TestQuestion.objects.create(test=test, **q)
        return section

    def update(self, instance: CourseSection, validated_data: dict) -> CourseSection:
        test_data = validated_data.pop("test", serializers.empty)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if test_data is not serializers.empty:
            if test_data is None:
                CourseTest.objects.filter(section=instance).delete()
            else:
                questions = test_data.pop("questions", None)
                test, _ = CourseTest.objects.update_or_create(
                    section=instance, defaults=test_data
                )
                if questions is not None:
                    test.questions.all().delete()
                    for q in questions:
                        TestQuestion.objects.create(test=test, **q)
        return instance


# --------------------------------------------------------------------------- #
# Course
# --------------------------------------------------------------------------- #
class CourseListSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    instructor_id = serializers.IntegerField(read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id", "title", "short_description", "description",
            "image_url", "price", "is_free", "category", "level",
            "status", "points_required_for_certificate",
            "objectives", "prerequisites",
            "instructor", "instructor_id", "progress",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "instructor", "instructor_id", "progress", "created_at", "updated_at")

    def get_progress(self, obj) -> float | None:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return None
        # Avoid circular import at module load time
        from apps.enrollments.models import Enrollment
        enrollment = Enrollment.objects.filter(user=user, course=obj).only("progress_percentage").first()
        return enrollment.progress_percentage if enrollment else None


class CourseDetailSerializer(CourseListSerializer):
    sections = CourseSectionSerializer(many=True, read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ("sections",)


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id", "title", "description", "short_description", "image_url",
            "price", "is_free", "category", "level", "status",
            "objectives", "prerequisites", "points_required_for_certificate",
        )
        read_only_fields = ("id",)
