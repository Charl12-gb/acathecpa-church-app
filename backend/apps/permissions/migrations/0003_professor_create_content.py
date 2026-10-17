"""Professors could edit and publish their articles/podcasts but not create them."""
from django.db import migrations


def grant(apps, schema_editor):
    Role = apps.get_model("app_permissions", "Role")
    Permission = apps.get_model("app_permissions", "Permission")
    RolePermission = apps.get_model("app_permissions", "RolePermission")
    role = Role.objects.filter(name="professor").first()
    if not role:
        return  # fresh database: seed_permissions will create it with the grant
    perm, _ = Permission.objects.get_or_create(
        permission="create_content",
        defaults={"title": "Create Content", "category": "Content Management"},
    )
    RolePermission.objects.get_or_create(role=role, permission=perm)


class Migration(migrations.Migration):
    dependencies = [("app_permissions", "0002_remove_student_edit_lesson")]

    operations = [migrations.RunPython(grant, migrations.RunPython.noop)]
