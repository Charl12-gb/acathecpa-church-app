"""
Admin and super admin journeys through the HTTP API with the real seeded roles:
user management under a strict hierarchy, deletion rules, professors,
dashboard, categories and the contact form.
"""
from __future__ import annotations

from datetime import datetime
from unittest import mock

import pytest
from django.core import mail
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import ContactMessage, User
from apps.courses.models import Category, Course, CourseStatus
from apps.enrollments.models import Certificate, Enrollment
from apps.payments.models import Payment, PaymentStatus
from apps.permissions.models import Permission, Role

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


def _client(user=None):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user)
    return client


@pytest.fixture
def people(roles):
    return {
        "admin": _user("admin@acathecpa.test", roles["admin"]),
        "super": _user("super@acathecpa.test", roles["super_admin"]),
        "student": _user("eleve@acathecpa.test", roles["student"], name="Awa Koné"),
        "prof": _user("prof@acathecpa.test", roles["professor"]),
    }


def _paid_course_with_history(prof, student):
    course = Course.objects.create(title="Fiscalité", instructor=prof, status=CourseStatus.PUBLISHED, price=5000)
    Payment.objects.create(user=student, course=course, amount=5000, status=PaymentStatus.COMPLETED)
    Enrollment.objects.create(user=student, course=course)
    Certificate.objects.create(user=student, course=course, verification_code="CERT-ADMIN00001")
    return course


# --------------------------------------------------------------------------- #
# Editing users
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("role_value", ["professor", {"name": "professor"}])
def test_admin_edits_a_user_and_changes_role(people, role_value):
    student = people["student"]
    resp = _client(people["admin"]).put(f"{API}/users/{student.id}", {
        "name": "Awa K.", "email": student.email, "phone": "", "role": role_value, "is_active": True,
    }, format="json")
    assert resp.status_code == 200, resp.data
    student.refresh_from_db()
    assert (student.name, student.role.name, student.phone) == ("Awa K.", "professor", None)


# --------------------------------------------------------------------------- #
# Hierarchy: an admin never acts on super admins
# --------------------------------------------------------------------------- #
def test_admin_cannot_touch_super_admin_accounts(people):
    admin, sup = people["admin"], people["super"]
    c = _client(admin)
    assert c.patch(f"{API}/users/{sup.id}", {"password": "Hijacked123!"}, format="json").status_code == 403
    assert c.patch(f"{API}/users/{sup.id}", {"is_active": False}, format="json").status_code == 403
    assert c.delete(f"{API}/users/{sup.id}").status_code == 403
    sup.refresh_from_db()
    assert sup.check_password("Password123!") and sup.is_active


def test_admin_cannot_hand_out_the_super_admin_role(people, roles):
    admin, student = people["admin"], people["student"]
    c = _client(admin)
    assert c.patch(f"{API}/users/{admin.id}", {"role": "super_admin"}, format="json").status_code == 403
    assert c.patch(f"{API}/users/{student.id}", {"role_id": roles["super_admin"].id}, format="json").status_code == 403
    resp = c.post(f"{API}/auth/register", {"email": "x@acathecpa.test", "password": "Password123!",
                                           "role": "super_admin"}, format="json")
    assert resp.status_code == 403
    admin.refresh_from_db()
    assert admin.role.name == "admin"
    assert not User.objects.filter(email="x@acathecpa.test").exists()
    # Other roles are still fine.
    assert c.post(f"{API}/auth/register", {"email": "y@acathecpa.test", "password": "Password123!",
                                           "role": "admin"}, format="json").status_code == 201


def test_roles_are_managed_by_super_admins_only(people, roles):
    admin_c, super_c = _client(people["admin"]), _client(people["super"])
    assert admin_c.get(f"{API}/permissions/roles/").status_code == 200
    assert admin_c.post(f"{API}/permissions/roles/", {"name": "moderateur"}, format="json").status_code == 403
    perm = Permission.objects.get(permission="create_content")
    link = {"role_id": roles["student"].id, "permission_id": perm.id}
    assert admin_c.post(f"{API}/permissions/role-permissions/", link, format="json").status_code == 403
    assert super_c.post(f"{API}/permissions/role-permissions/", link, format="json").status_code == 201
    assert super_c.patch(f"{API}/users/{people['student'].id}", {"role": "super_admin"}, format="json").status_code == 200


# --------------------------------------------------------------------------- #
# Deleting users
# --------------------------------------------------------------------------- #
def test_admin_must_deactivate_an_account_with_history(people):
    student, prof = people["student"], people["prof"]
    _paid_course_with_history(prof, student)
    c = _client(people["admin"])

    impact = c.get(f"{API}/users/{student.id}/deletion-impact").data
    assert impact["has_history"] and not impact["can_delete"]
    assert impact["history"]["payments"] == 1 and impact["history"]["certificates"] == 1

    for user in (student, prof):
        resp = c.delete(f"{API}/users/{user.id}")
        assert resp.status_code == 409
        assert "désactivez" in resp.data["detail"]
    assert Payment.objects.count() == 1 and Certificate.objects.count() == 1

    assert c.patch(f"{API}/users/{student.id}", {"is_active": False}, format="json").status_code == 200


def test_admin_deletes_an_account_without_history(people, roles):
    newcomer = _user("nouveau@acathecpa.test", roles["student"])
    c = _client(people["admin"])
    assert c.get(f"{API}/users/{newcomer.id}/deletion-impact").data["can_delete"] is True
    assert c.delete(f"{API}/users/{newcomer.id}").status_code == 200
    assert not User.objects.filter(pk=newcomer.id).exists()


def test_super_admin_deletes_a_professor_permanently_with_data(people):
    student, prof = people["student"], people["prof"]
    course = _paid_course_with_history(prof, student)
    c = _client(people["super"])

    impact = c.get(f"{API}/users/{prof.id}/deletion-impact").data
    assert impact["can_delete"] and impact["history"]["courses"] == 1 and impact["history"]["course_enrollments"] == 1

    assert c.delete(f"{API}/users/{prof.id}").status_code == 200
    assert not User.objects.filter(pk=prof.id).exists()
    assert not Course.objects.filter(pk=course.id).exists()
    assert (Payment.objects.count(), Certificate.objects.count(), Enrollment.objects.count()) == (0, 0, 0)
    assert User.objects.filter(pk=student.id).exists()  # the student keeps their account


def test_super_admin_deletes_a_student_permanently_with_data(people):
    student = people["student"]
    _paid_course_with_history(people["prof"], student)
    assert _client(people["super"]).delete(f"{API}/users/{student.id}").status_code == 200
    assert (Payment.objects.count(), Certificate.objects.count()) == (0, 0)


def test_nobody_deletes_their_own_account_here(people):
    assert _client(people["super"]).delete(f"{API}/users/{people['super'].id}").status_code == 403


# --------------------------------------------------------------------------- #
# Professors
# --------------------------------------------------------------------------- #
def test_professors_without_phone_and_welcome_email(people):
    c = _client(people["admin"])
    for email in ("p1@acathecpa.test", "p2@acathecpa.test"):
        resp = c.post(f"{API}/professors/", {"email": email, "password": "Password123!", "name": "Prof",
                                             "phone": "", "specialization": "Audit"}, format="json")
        assert resp.status_code == 201, resp.data
    assert User.objects.filter(email__in=["p1@acathecpa.test", "p2@acathecpa.test"], phone__isnull=True).count() == 2

    welcome = mail.outbox[-1]
    assert welcome.to == ["p2@acathecpa.test"] and "compte formateur" in welcome.subject
    token = welcome.body.split("reset-password?token=")[1].split()[0]
    resp = APIClient().post(f"{API}/auth/reset-password", {"token": token, "new_password": "MonNouveau123!"}, format="json")
    assert resp.status_code == 200
    assert User.objects.get(email="p2@acathecpa.test").check_password("MonNouveau123!")

    c.post(f"{API}/professors/", {"email": "p3@acathecpa.test", "password": "Password123!", "name": "P",
                                  "phone": "+22501020304", "specialization": "Audit"}, format="json")
    resp = c.post(f"{API}/professors/", {"email": "p4@acathecpa.test", "password": "Password123!", "name": "P",
                                         "phone": "+22501020304", "specialization": "Audit"}, format="json")
    assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# Dashboard, categories, contact
# --------------------------------------------------------------------------- #
def test_dashboard_dates_are_readable_and_months_are_calendar_months(people):
    Course.objects.create(title="C", instructor=people["prof"])
    c = _client(people["admin"])
    for activity in c.get(f"{API}/admin/dashboard/recent-activities").data:
        datetime.fromisoformat(activity["timestamp"])  # raises on "…+00:00Z"
    months = [m["month"] for m in c.get(f"{API}/admin/dashboard/monthly-registrations").data]
    assert len(months) == 6 and len(set(months)) == 6


def test_category_rename_follows_courses_and_used_category_is_kept(people):
    cat = Category.objects.create(name="Compta")
    course = Course.objects.create(title="C", instructor=people["prof"], category="Compta")
    c = _client(people["admin"])
    assert c.patch(f"{API}/categories/{cat.id}", {"name": "Comptabilité"}, format="json").status_code == 200
    course.refresh_from_db()
    assert course.category == "Comptabilité"
    assert c.delete(f"{API}/categories/{cat.id}").status_code == 409
    Course.objects.all().delete()
    assert c.delete(f"{API}/categories/{cat.id}").status_code == 204


def test_contact_message_is_kept_even_when_the_email_fails(db):
    payload = {"name": "Koffi", "email": "koffi@exemple.test", "subject": "Inscription", "message": "Bonjour"}
    resp = APIClient().post(f"{API}/contact", payload, format="json")
    assert resp.status_code == 201
    assert mail.outbox[-1].reply_to == ["koffi@exemple.test"]

    with mock.patch("django.core.mail.EmailMessage.send", side_effect=OSError("SMTP down")):
        resp = APIClient().post(f"{API}/contact", {**payload, "subject": "Facture"}, format="json")
    assert resp.status_code == 201 and "reçu" in resp.data["message"]
    kept = ContactMessage.objects.get(subject="Facture")
    assert kept.email_sent is False and kept.message == "Bonjour"
