"""
Create a default super-admin user.

Equivalent of FastAPI `seed_default_user`.

Usage::

    python manage.py seed_default_user --email admin@acathecpa.local --password Admin123!
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.permissions.models import Role


class Command(BaseCommand):
    help = "Create or update a default super-admin user."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--name", default="Super Admin")

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        name = options["name"]

        role, created = Role.objects.get_or_create(name="super_admin")
        if created:
            self.stdout.write(self.style.SUCCESS(f"  + Role 'super_admin' created (id={role.id})"))

        user = User.objects.filter(email=email).first()
        if user:
            user.name = name
            user.role = role
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.WARNING(
                f"  ~ User {email} already existed — credentials & role updated."
            ))
            return

        user = User(email=email, name=name, role=role, is_active=True)
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("  Default super-admin created"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(f"  id       : {user.id}")
        self.stdout.write(f"  email    : {email}")
        self.stdout.write(f"  password : {password}")
        self.stdout.write(self.style.WARNING(
            "  /!\\ Change the password after the first login."
        ))
