"""
Visitor-facing guarantees: premium content and authors' data stay private,
brute force and spam are slowed down, emails are confirmed, reset links are
single-use.
"""
from __future__ import annotations

import pytest
from django.core import mail
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.models import ContactMessage, User
from apps.content.models import Content
from apps.payments.models import Payment, PaymentStatus
from apps.permissions.models import Role

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


def _rows(resp):
    return resp.data["results"] if isinstance(resp.data, dict) else resp.data


# --------------------------------------------------------------------------- #
# Articles and podcasts
# --------------------------------------------------------------------------- #
@pytest.fixture
def contents(roles):
    author = _user("auteur@acathecpa.test", roles["professor"], phone="+22990000000", birthdate="1980-01-01")
    premium = Content.objects.create(title="Fiscalité avancée", type="podcast", content_body="Transcription payante",
                                     media_url="https://cdn.test/episode.mp3", is_premium=True, price=2000,
                                     author=author, status="published")
    free = Content.objects.create(title="La TVA en bref", type="article", content_body="Texte libre",
                                  author=author, status="published")
    return author, premium, free


def _by_title(resp):
    return {row["title"]: row for row in _rows(resp)}


def test_public_list_hides_premium_content_and_author_details(contents):
    rows = _by_title(APIClient().get(f"{API}/contents/"))
    premium, free = rows["Fiscalité avancée"], rows["La TVA en bref"]
    assert (premium["content_body"], premium["media_url"], premium["requires_payment"]) == (None, None, True)
    assert (free["content_body"], free["requires_payment"]) == ("Texte libre", False)
    assert set(premium["author"]) == {"id", "name", "professor_profile"}


def test_buyers_and_author_see_premium_content_in_the_list(contents, roles):
    author, premium, _ = contents
    buyer = _user("acheteur@acathecpa.test", roles["student"])
    other = _user("curieux@acathecpa.test", roles["student"])
    Payment.objects.create(user=buyer, content=premium, amount=2000, status=PaymentStatus.COMPLETED)

    for user, visible in ((buyer, True), (author, True), (other, False)):
        row = _by_title(_client(user).get(f"{API}/contents/"))["Fiscalité avancée"]
        assert (row["media_url"] == "https://cdn.test/episode.mp3") is visible


def test_content_detail_hides_author_details(contents):
    _, _, free = contents
    author = APIClient().get(f"{API}/contents/{free.id}").data["author"]
    assert "email" not in author and "phone" not in author


# --------------------------------------------------------------------------- #
# Login attempts
# --------------------------------------------------------------------------- #
def _login(email, password, ip="10.0.0.1"):
    return APIClient(REMOTE_ADDR=ip).post(f"{API}/auth/login", {"username": email, "password": password})


def test_five_failed_logins_lock_the_account_from_that_address(roles):
    _user("eleve@acathecpa.test", roles["student"])
    _user("voisin@acathecpa.test", roles["student"])
    for _ in range(5):
        assert _login("eleve@acathecpa.test", "mauvais").status_code == 401
    blocked = _login("eleve@acathecpa.test", "Password123!")
    assert blocked.status_code == 429 and "15 minutes" in blocked.data["detail"]

    # Someone else on the same network, or the owner elsewhere, is not blocked.
    assert _login("voisin@acathecpa.test", "Password123!").status_code == 200
    assert _login("eleve@acathecpa.test", "Password123!", ip="10.0.0.2").status_code == 200


def test_a_successful_login_resets_the_counter(roles):
    _user("eleve@acathecpa.test", roles["student"])
    for _ in range(4):
        _login("eleve@acathecpa.test", "mauvais")
    assert _login("eleve@acathecpa.test", "Password123!").status_code == 200
    for _ in range(4):
        _login("eleve@acathecpa.test", "mauvais")
    assert _login("eleve@acathecpa.test", "Password123!").status_code == 200


def test_an_address_trying_many_accounts_is_slowed_down(roles):
    _user("cible@acathecpa.test", roles["student"])
    for i in range(30):
        _login(f"inconnu{i}@acathecpa.test", "x")
    assert _login("cible@acathecpa.test", "Password123!").status_code == 429


# --------------------------------------------------------------------------- #
# Contact form
# --------------------------------------------------------------------------- #
MESSAGE = {"name": "Koffi", "email": "koffi@exemple.test", "subject": "Inscription", "message": "Bonjour"}


def test_contact_honeypot_drops_robots_silently(db):
    resp = APIClient().post(f"{API}/contact", {**MESSAGE, "website": "http://spam.test"}, format="json")
    assert resp.status_code == 201
    assert not ContactMessage.objects.exists() and not mail.outbox


def test_contact_is_limited_per_address(db):
    client = APIClient(REMOTE_ADDR="10.0.0.9")
    for _ in range(5):
        assert client.post(f"{API}/contact", MESSAGE, format="json").status_code == 201
    assert client.post(f"{API}/contact", MESSAGE, format="json").status_code == 429
    assert ContactMessage.objects.count() == 5


# --------------------------------------------------------------------------- #
# Email confirmation and reset links
# --------------------------------------------------------------------------- #
def _token_from(body, marker):
    return body.split(marker)[1].split()[0]


def test_sign_up_sends_a_confirmation_link_and_login_works_meanwhile(roles):
    resp = APIClient().post(f"{API}/auth/register", {"email": "awa@acathecpa.test", "name": "Awa",
                                                     "password": "Password123!"}, format="json")
    assert resp.status_code == 201 and resp.data["email_verified"] is False
    assert _login("awa@acathecpa.test", "Password123!").status_code == 200

    token = _token_from(mail.outbox[-1].body, "verify-email?token=")
    assert APIClient().post(f"{API}/auth/verify-email", {"token": "faux"}, format="json").status_code == 400
    assert APIClient().post(f"{API}/auth/verify-email", {"token": token}, format="json").status_code == 200
    assert User.objects.get(email="awa@acathecpa.test").email_verified is True


def test_confirmation_link_can_be_sent_again(roles):
    user = _user("awa@acathecpa.test", roles["student"])
    resp = _client(user).post(f"{API}/auth/resend-verification")
    assert resp.status_code == 200 and "awa@acathecpa.test" in resp.data["message"]
    assert "verify-email?token=" in mail.outbox[-1].body


def test_reset_link_works_once_and_confirms_the_address(roles):
    user = _user("awa@acathecpa.test", roles["student"])
    APIClient().post(f"{API}/auth/forgot-password", {"email": user.email}, format="json")
    token = _token_from(mail.outbox[-1].body, "reset-password?token=")

    first = APIClient().post(f"{API}/auth/reset-password", {"token": token, "new_password": "Nouveau123!"}, format="json")
    assert first.status_code == 200
    second = APIClient().post(f"{API}/auth/reset-password", {"token": token, "new_password": "Pirate123!"}, format="json")
    assert second.status_code == 400
    user.refresh_from_db()
    assert user.check_password("Nouveau123!") and user.email_verified is True
