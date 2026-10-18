"""
Who may manage whom.

    super_admin : everything, including other super admins (but not deleting
                  themselves) and the permanent deletion of an account.
    admin       : students, professors and other admins, never a super admin
                  account and never the super_admin role.
"""
from __future__ import annotations

from typing import Optional

SUPER_ADMIN = "super_admin"
ADMIN = "admin"


def role_name(user) -> Optional[str]:
    role = getattr(user, "role", None)
    return role.name if role else None


def is_super_admin(user) -> bool:
    return bool(user and (getattr(user, "is_superuser", False) or role_name(user) == SUPER_ADMIN))


def is_last_active_super_admin(user) -> bool:
    """True if `user` is the only active super admin left."""
    from .models import User

    if role_name(user) != SUPER_ADMIN or not user.is_active:
        return False
    return not User.objects.filter(role__name=SUPER_ADMIN, is_active=True).exclude(pk=user.pk).exists()


def can_manage_user(actor, target) -> bool:
    """Edit, (de)activate or delete `target`."""
    if is_super_admin(actor):
        return True
    return role_name(target) != SUPER_ADMIN


def can_assign_role(actor, new_role_name: Optional[str]) -> bool:
    if not new_role_name:
        return True
    return is_super_admin(actor) or new_role_name != SUPER_ADMIN


def account_history(user) -> dict:
    """What deleting `user` would destroy, by kind."""
    from apps.content.models import Content
    from apps.courses.models import Course
    from apps.enrollments.models import Certificate, Enrollment
    from apps.live_sessions.models import LiveSession
    from apps.payments.models import Payment

    return {
        "enrollments": Enrollment.objects.filter(user=user).count(),
        "payments": Payment.objects.filter(user=user).count(),
        "certificates": Certificate.objects.filter(user=user).count(),
        "courses": Course.objects.filter(instructor=user).count(),
        "course_enrollments": Enrollment.objects.filter(course__instructor=user).count(),
        "contents": Content.objects.filter(author=user).count(),
        "live_sessions": LiveSession.objects.filter(host=user).count(),
    }


def delete_account_with_data(user) -> None:
    """
    Permanent deletion (super admin only): the account, its courses and
    everything attached to them, its payments and certificates.
    Payments and certificates are protected from cascades, so they go first.
    """
    from django.db import transaction
    from django.db.models import Q

    from apps.enrollments.models import Certificate
    from apps.payments.models import Payment

    with transaction.atomic():
        Payment.objects.filter(Q(user=user) | Q(course__instructor=user)).delete()
        Certificate.objects.filter(Q(user=user) | Q(course__instructor=user)).delete()
        user.delete()
