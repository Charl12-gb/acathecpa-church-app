"""
Seed roles, permissions and role/permission links from
`apps.permissions.permission_definitions.ROLES_PERMISSIONS_DATA`.

Usage::

    python manage.py seed_permissions          # safe to re-run on every deploy
    python manage.py seed_permissions --sync   # also restore removed links

By default a link is only created for a role created now, or for a permission
that did not exist yet (a new feature). A permission the super admin removed
from a role is therefore not granted back by the next deploy. `--sync` restores
every link of the definitions file.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.permissions.models import Permission, Role, RolePermission
from apps.permissions.permission_definitions import ROLES_PERMISSIONS_DATA


class Command(BaseCommand):
    help = "Seed roles, permissions and role-permission assignments."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Restore every role/permission link of the definitions (undoes manual removals).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        sync = options.get("sync", False)
        created_perms = 0
        created_roles = 0
        created_links = 0

        defined = {p["permission"] for perms in ROLES_PERMISSIONS_DATA.values() for p in perms}
        new_permissions = defined - set(
            Permission.objects.filter(permission__in=defined).values_list("permission", flat=True)
        )

        for role_name, perms in ROLES_PERMISSIONS_DATA.items():
            role, role_created = Role.objects.get_or_create(name=role_name)
            if role_created:
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

                if sync or role_created or perm["permission"] in new_permissions:
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
