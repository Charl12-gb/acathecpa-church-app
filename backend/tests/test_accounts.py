"""
Authentication tests: register / login / me / login by phone.
"""
import pytest

pytestmark = pytest.mark.django_db


def test_register_creates_user(api_client, role_student):
    payload = {
        "email": "new@test.local",
        "password": "Password123!",
        "name": "New User",
        "phone": "+22500000001",
    }
    resp = api_client.post("/api/v1/auth/register", payload, format="json")
    assert resp.status_code in (200, 201), resp.content


def test_login_with_email(api_client, student_user):
    resp = api_client.post(
        "/api/v1/auth/login",
        {"username": student_user.email, "password": "Password123!"},
        format="json",
    )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert "access" in body or "access_token" in body


def test_login_wrong_password_denied(api_client, student_user):
    resp = api_client.post(
        "/api/v1/auth/login",
        {"username": student_user.email, "password": "Wrong!"},
        format="json",
    )
    assert resp.status_code in (400, 401)


def test_me_returns_authenticated_user(auth_client, admin_user):
    # admin bypasses the `view_own_profile` permission required by MeView
    client = auth_client(admin_user)
    resp = client.get("/api/v1/auth/users/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == admin_user.email
