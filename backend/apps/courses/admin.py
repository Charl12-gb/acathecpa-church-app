from django.contrib import admin

from .models import Course, CourseLesson, CourseSection, CourseTest, TestQuestion


class CourseLessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 0


class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 0
    show_change_link = True


class TestQuestionInline(admin.TabularInline):
    model = TestQuestion
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "instructor", "status", "is_free", "price", "created_at")
    list_filter = ("status", "is_free", "category", "level")
    search_fields = ("title", "description", "category")
    inlines = [CourseSectionInline]


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "order", "content_type")
    list_filter = ("content_type",)
    search_fields = ("title", "course__title")
    inlines = [CourseLessonInline]


@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "section", "order", "type")
    list_filter = ("type",)
    search_fields = ("title",)


@admin.register(CourseTest)
class CourseTestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "section", "passing_score", "max_attempts")
    inlines = [TestQuestionInline]


@admin.register(TestQuestion)
class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "test", "question_type", "points")
    list_filter = ("question_type",)
