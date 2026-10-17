"""Students were seeded with edit_course_lesson by mistake; revoke it."""
from django.db import migrations


def revoke(apps, schema_editor):
    RolePermission = apps.get_model("app_permissions", "RolePermission")
    RolePermission.objects.filter(
        role__name="student", permission__permission="edit_course_lesson"
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("app_permissions", "0001_initial")]

    operations = [migrations.RunPython(revoke, migrations.RunPython.noop)]
