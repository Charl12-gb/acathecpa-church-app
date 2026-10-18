"""
Super admin journey: fixed system roles, permissions and overrides, the last
super admin, the seed, the audit log and changing one's own password.
"""
from __future__ import annotations

import pytest
from django.core import mail
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.courses.models import Course, CourseStatus
from apps.enrollments.models import Enrollment
from apps.permissions.models import Permission, Role, RolePermission, UserPermission
from apps.permissions.permissions import check_permission

API = "/api/v1"


@pytest.fixture
def roles(db):
    call_command("seed_permissions", verbosity=0)
    return {r.name: r for r in Role.objects.all()}


def _user(email, role, **extra):
    user = User(email=email, name=extra.pop("name", email.split("@")[0].title()), role=role, **extra)
    user.set_password("Password123!")
    user.save()
    return user


def _client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def sup(roles):
    return _user("super@acathecpa.test", roles["super_admin"], name="Super Admin")


# --------------------------------------------------------------------------- #
# Roles are fixed
# --------------------------------------------------------------------------- #
def test_system_roles_cannot_be_created_renamed_or_deleted(sup, roles):
    c = _client(sup)
    assert c.post(f"{API}/permissions/roles/", {"name": "moderateur"}, format="json").status_code == 400
    assert c.patch(f"{API}/permissions/roles/{roles['super_admin'].id}/", {"name": "chef"}, format="json").status_code == 400
    assert c.delete(f"{API}/permissions/roles/{roles['student'].id}/").status_code == 400
    assert set(Role.objects.values_list("name", flat=True)) == {"student", "professor", "admin", "super_admin"}


def test_a_leftover_custom_role_is_deleted_only_once_unused(sup, roles):
    legacy = Role.objects.create(name="ancien-role")
    member = _user("m@acathecpa.test", legacy)
    c = _client(sup)
    assert c.delete(f"{API}/permissions/roles/{legacy.id}/").status_code == 400
    member.role = roles["student"]
    member.save()
    assert c.delete(f"{API}/permissions/roles/{legacy.id}/").status_code == 204


def test_permission_definitions_are_read_only(sup):
    c = _client(sup)
    assert c.get(f"{API}/permissions/permissions/").status_code == 200
    assert c.post(f"{API}/permissions/permissions/", {"permission": "x", "title": "X", "category": "Y"},
                  format="json").status_code == 405


# --------------------------------------------------------------------------- #
# Permissions of a role, overrides for one person
# --------------------------------------------------------------------------- #
def test_super_admin_grants_and_revokes_a_role_permission(sup, roles):
    student = _user("eleve@acathecpa.test", roles["student"])
    perm = Permission.objects.get(permission="create_content")
    c = _client(sup)
    link = {"role_id": roles["student"].id, "permission_id": perm.id}

    resp = c.post(f"{API}/permissions/role-permissions/", link, format="json")
    assert resp.status_code == 201 and check_permission(student, "create_content")
    assert c.post(f"{API}/permissions/role-permissions/", link, format="json").status_code == 200  # no duplicate
    assert RolePermission.objects.filter(role=roles["student"], permission=perm).count() == 1

    assert c.delete(f"{API}/permissions/role-permissions/{resp.data['id']}/").status_code == 204
    assert not check_permission(student, "create_content")
    actions = list(AuditLog.objects.order_by("id").values_list("action", "target_label", "details"))
    assert actions == [
        ("role.permission_granted", "student", {"permission": "create_content"}),
        ("role.permission_revoked", "student", {"permission": "create_content"}),
    ]


def test_user_override_adds_a_permission_to_one_person(sup, roles):
    student = _user("eleve@acathecpa.test", roles["student"])
    perm = Permission.objects.get(permission="create_content")
    c = _client(sup)
    payload = {"user": student.id, "permission_id": perm.id, "type": "Add"}

    resp = c.post(f"{API}/permissions/user-permissions/", payload, format="json")
    assert resp.status_code == 201, resp.data
    assert resp.data["user_email"] == "eleve@acathecpa.test"
    assert check_permission(student, "create_content")
    assert c.post(f"{API}/permissions/user-permissions/", payload, format="json").status_code == 400

    assert c.get(f"{API}/permissions/user-permissions/", {"user": student.id}).data[0]["permission"]["permission"] == "create_content"
    assert c.delete(f"{API}/permissions/user-permissions/{resp.data['id']}/").status_code == 204
    assert not UserPermission.objects.exists()
    assert AuditLog.objects.filter(action="user.permission_override_removed", target_label=student.email).exists()


# --------------------------------------------------------------------------- #
# There is always a super admin
# --------------------------------------------------------------------------- #
def test_the_last_super_admin_cannot_leave(sup, roles):
    c = _client(sup)
    assert c.patch(f"{API}/users/{sup.id}", {"role": "admin"}, format="json").status_code == 400
    assert c.patch(f"{API}/users/{sup.id}", {"is_active": False}, format="json").status_code == 400

    _user("second@acathecpa.test", roles["super_admin"])
    assert c.patch(f"{API}/users/{sup.id}", {"role": "admin"}, format="json").status_code == 200


def test_createsuperuser_gets_the_super_admin_role(roles):
    user = User.objects.create_superuser(email="root@acathecpa.test", password="Password123!")
    assert user.role.name == "super_admin"


# --------------------------------------------------------------------------- #
# Seed
# --------------------------------------------------------------------------- #
def test_seed_keeps_removals_but_grants_new_permissions(roles):
    RolePermission.objects.filter(role=roles["student"], permission__permission="enroll_in_course").delete()
    Permission.objects.filter(permission="create_content").delete()  # as if newly added in code

    call_command("seed_permissions", verbosity=0)
    assert not RolePermission.objects.filter(role=roles["student"], permission__permission="enroll_in_course").exists()
    assert RolePermission.objects.filter(role=roles["professor"], permission__permission="create_content").exists()

    call_command("seed_permissions", "--sync", verbosity=0)
    assert RolePermission.objects.filter(role=roles["student"], permission__permission="enroll_in_course").exists()


# --------------------------------------------------------------------------- #
# Audit log
# --------------------------------------------------------------------------- #
def test_sensitive_account_actions_are_logged_for_super_admins(sup, roles):
    admin = _user("admin@acathecpa.test", roles["admin"])
    prof = _user("prof@acathecpa.test", roles["professor"])
    student = _user("eleve@acathecpa.test", roles["student"])
    course = Course.objects.create(title="Fiscalité", instructor=prof, status=CourseStatus.PUBLISHED, is_free=True)
    Enrollment.objects.create(user=student, course=course)

    a = _client(admin)
    a.patch(f"{API}/users/{student.id}", {"role": "professor"}, format="json")
    a.patch(f"{API}/users/{student.id}", {"is_active": False, "password": "Nouveau123!"}, format="json")
    _client(sup).delete(f"{API}/users/{prof.id}")

    assert a.get(f"{API}/audit-logs").status_code == 403
    entries = _client(sup).get(f"{API}/audit-logs").data
    summary = [(e["actor_email"], e["action"], e["target_label"]) for e in reversed(entries)]
    assert summary == [
        ("admin@acathecpa.test", "user.role_changed", "eleve@acathecpa.test"),
        ("admin@acathecpa.test", "user.deactivated", "eleve@acathecpa.test"),
        ("admin@acathecpa.test", "user.password_reset", "eleve@acathecpa.test"),
        ("super@acathecpa.test", "user.deleted_with_data", "prof@acathecpa.test"),
    ]
    deletion = entries[0]
    assert deletion["action_label"] == "Compte supprimé définitivement avec ses données"
    assert deletion["details"]["history"]["courses"] == 1
    assert entries[-1]["details"] == {"old": "student", "new": "professor"}

    filtered = _client(sup).get(f"{API}/audit-logs", {"action": "user.deactivated"}).data
    assert [e["action"] for e in filtered] == ["user.deactivated"]


# --------------------------------------------------------------------------- #
# Own password
# --------------------------------------------------------------------------- #
def test_users_change_their_own_password(sup):
    c = _client(sup)
    wrong = c.post(f"{API}/auth/change-password", {"current_password": "mauvais", "new_password": "Nouveau123!"}, format="json")
    assert wrong.status_code == 400
    ok = c.post(f"{API}/auth/change-password", {"current_password": "Password123!", "new_password": "Nouveau123!"}, format="json")
    assert ok.status_code == 200
    sup.refresh_from_db()
    assert sup.check_password("Nouveau123!")
    assert mail.outbox[-1].to == ["super@acathecpa.test"] and "modifié" in mail.outbox[-1].subject
