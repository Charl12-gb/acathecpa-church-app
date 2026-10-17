"""
The course editor used to save a video lesson's URL as its text body
(content_body) instead of video_url, so students never got a player.
Move those URLs to video_url.
"""
from django.db import migrations


def move_urls(apps, schema_editor):
    CourseLesson = apps.get_model("courses", "CourseLesson")
    for lesson in CourseLesson.objects.filter(type="video").exclude(content_body__isnull=True):
        body = (lesson.content_body or "").strip()
        if not lesson.video_url and body.startswith(("http://", "https://")) and " " not in body:
            lesson.video_url = body
            lesson.content_body = None
            lesson.save(update_fields=["video_url", "content_body"])


class Migration(migrations.Migration):
    dependencies = [("courses", "0004_alter_testquestion_question_type")]

    operations = [migrations.RunPython(move_urls, migrations.RunPython.noop)]
