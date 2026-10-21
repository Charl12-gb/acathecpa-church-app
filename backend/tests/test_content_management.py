"""
Posts: file uploads in both formats, and admins managing everyone's posts.
"""
from __future__ import annotations

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.content.models import Content
from apps.permissions.models import Role

API = "/api/v1"


@pytest.fixture
def roles(db):
    call_command("seed_permissions", verbosity=0)
    return {r.name: r for r in Role.objects.all()}


def _user(email, role):
    return User.objects.create(email=email, name=email.split("@")[0].title(), role=role)


def _client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def media(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        yield tmp_path


# --------------------------------------------------------------------------- #
# Uploads
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("filename,content_type,category", [
    ("calendrier fiscal.pdf", "application/pdf", "document"),
    ("episode.mp3", "audio/mpeg", "audio"),
    ("cours.mp4", "video/mp4", "video"),
])
def test_raw_upload_for_hosts_that_block_multipart(roles, media, filename, content_type, category):
    prof = _user("prof@acathecpa.test", roles["professor"])
    resp = _client(prof).generic(
        "POST", f"{API}/uploads/?filename={filename}&category={category}",
        data=b"x" * 4096, content_type=content_type,
    )
    assert resp.status_code == 201, resp.data
    path = resp.data["url"].split("/media/", 1)[1]  # absolute URL to the stored file
    assert path.startswith(f"uploads/{category}/")
    assert resp.data["original_name"] == filename
    assert (media / path).stat().st_size == 4096


def test_multipart_upload_still_works(roles, media):
    prof = _user("prof@acathecpa.test", roles["professor"])
    upload = SimpleUploadedFile("doc.pdf", b"%PDF-1.4", content_type="application/pdf")
    resp = _client(prof).post(f"{API}/uploads/", {"file": upload, "category": "document"}, format="multipart")
    assert resp.status_code == 201


def test_raw_upload_checks_the_extension(roles, media):
    prof = _user("prof@acathecpa.test", roles["professor"])
    resp = _client(prof).generic("POST", f"{API}/uploads/?filename=script.exe&category=document",
                                 data=b"MZ", content_type="application/octet-stream")
    assert resp.status_code == 400


def test_upload_requires_login(db, media):
    resp = APIClient().generic("POST", f"{API}/uploads/?filename=a.pdf", data=b"x", content_type="application/pdf")
    assert resp.status_code == 401


# --------------------------------------------------------------------------- #
# Admins manage every post
# --------------------------------------------------------------------------- #
@pytest.fixture
def posts(roles):
    prof = _user("prof@acathecpa.test", roles["professor"])
    other = _user("autre@acathecpa.test", roles["professor"])
    draft = Content.objects.create(title="Brouillon TVA", type="article", format="text", status="draft",
                                   content_body="<p>En cours</p>", author=prof)
    premium = Content.objects.create(title="Podcast premium", type="podcast", format="audio", status="published",
                                     is_premium=True, price=2000, media_url="/media/uploads/audio/x.mp3",
                                     content_body="<p>Transcription</p>", author=other)
    return prof, other, draft, premium


@pytest.mark.parametrize("role", ["admin", "super_admin"])
def test_admins_list_every_post_with_filters(roles, posts, role):
    admin = _user(f"{role}@acathecpa.test", roles[role])
    c = _client(admin)
    titles = {row["title"] for row in c.get(f"{API}/contents/all/").data}
    assert titles == {"Brouillon TVA", "Podcast premium"}
    assert [r["title"] for r in c.get(f"{API}/contents/all/", {"status": "draft"}).data] == ["Brouillon TVA"]
    assert [r["title"] for r in c.get(f"{API}/contents/all/", {"q": "autre@"}).data] == ["Podcast premium"]


def test_others_cannot_list_every_post(roles, posts):
    prof = posts[0]
    assert _client(prof).get(f"{API}/contents/all/").status_code == 403
    assert APIClient().get(f"{API}/contents/all/").status_code == 401


def test_admin_opens_a_premium_post_in_full_before_editing_it(roles, posts):
    admin = _user("admin@acathecpa.test", roles["admin"])
    premium = posts[3]
    data = _client(admin).get(f"{API}/contents/{premium.id}").data
    assert data["content_body"] == "<p>Transcription</p>" and data["requires_payment"] is False


def test_admin_edits_changes_status_and_deletes_someone_elses_post(roles, posts):
    prof, _, draft, premium = posts
    admin = _user("admin@acathecpa.test", roles["admin"])
    c = _client(admin)

    resp = c.put(f"{API}/contents/{draft.id}", {
        "title": "TVA : le guide", "description": "", "content_body": "<p>Relu</p>", "type": "article",
        "format": "text", "media_url": None, "is_premium": False, "price": None, "status": "draft", "tags": [],
    }, format="json")
    assert resp.status_code == 200, resp.data
    draft.refresh_from_db()
    assert (draft.title, draft.author_id) == ("TVA : le guide", prof.id)  # author unchanged

    assert c.patch(f"{API}/contents/{draft.id}", {"status": "published"}, format="json").status_code == 200
    draft.refresh_from_db()
    assert draft.status == "published"

    assert c.delete(f"{API}/contents/{premium.id}").status_code == 204
    assert not Content.objects.filter(pk=premium.id).exists()

    actions = list(AuditLog.objects.order_by("id").values_list("action", "target_label"))
    assert actions == [("content.status_changed", "TVA : le guide"), ("content.deleted", "Podcast premium")]


def test_a_professor_still_cannot_touch_someone_elses_post(roles, posts):
    _, other, draft, _ = posts
    c = _client(other)
    assert c.patch(f"{API}/contents/{draft.id}", {"status": "published"}, format="json").status_code == 403
    assert c.delete(f"{API}/contents/{draft.id}").status_code == 403
