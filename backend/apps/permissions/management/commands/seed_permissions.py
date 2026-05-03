"""
Seed roles, permissions and role/permission links from
`apps.permissions.permission_definitions.ROLES_PERMISSIONS_DATA`.

Usage::

    python manage.py seed_permissions
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.permissions.models import Permission, Role, RolePermission
from apps.permissions.permission_definitions import ROLES_PERMISSIONS_DATA


class Command(BaseCommand):
    help = "Seed roles, permissions and role-permission assignments."

    @transaction.atomic
    def handle(self, *args, **options):
        created_perms = 0
        created_roles = 0
        created_links = 0

        for role_name, perms in ROLES_PERMISSIONS_DATA.items():
            role, was_created = Role.objects.get_or_create(name=role_name)
            if was_created:
                created_roles += 1

            for perm in perms:
                permission_obj, perm_created = Permission.objects.get_or_create(
                    permission=perm["permission"],
                    defaults={"title": perm["title"], "category": perm["category"]},
                )
                if perm_created:
                    created_perms += 1
                else:
                    # Keep title/category in sync with the source of truth.
                    changed = False
                    if permission_obj.title != perm["title"]:
                        permission_obj.title = perm["title"]
                        changed = True
                    if permission_obj.category != perm["category"]:
                        permission_obj.category = perm["category"]
                        changed = True
                    if changed:
                        permission_obj.save(update_fields=["title", "category"])

                _, link_created = RolePermission.objects.get_or_create(
                    role=role, permission=permission_obj
                )
                if link_created:
                    created_links += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding done. Roles created: {created_roles} | "
                f"Permissions created: {created_perms} | "
                f"Links created: {created_links}"
            )
        )
