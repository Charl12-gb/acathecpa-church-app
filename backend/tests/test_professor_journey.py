"""
Professor journey through the HTTP API with the real seeded roles: build a
course, quizzes, publish, follow students, run live sessions, write content,
and the guards that protect students' data.
"""
from __future__ import annotations

from datetime import timedelta

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import ProfessorProfile, User
from apps.courses.models import (
    Course,
    CourseLesson,
    CourseSection,
    CourseStatus,
    CourseTest,
    LessonType,
)
from apps.courses.models import TestQuestion as Question
from apps.enrollments.models import Certificate, Enrollment
from apps.live_sessions.models import LiveSession
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


@pytest.fixture
def prof(roles):
    user = _user("prof@acathecpa.test", roles["professor"], name="Aminata Diallo",
                 phone="+22500000001", birthdate="1980-01-01")
    ProfessorProfile.objects.create(user=user, specialization="Comptabilité", bio="Expert-comptable")
    return user


@pytest.fixture
def student(roles):
    return _user("eleve@acathecpa.test", roles["student"], name="Awa Koné")


def _course_with_quiz(prof, **extra):
    course = Course.objects.create(title="Fiscalité", instructor=prof, **extra)
    section = CourseSection.objects.create(course=course, title="Quiz", order=1, content_type="quiz")
    lesson = CourseLesson.objects.create(section=section, title="Intro", type=LessonType.TEXT, order=1)
    test = CourseTest.objects.create(section=section, title="Quiz TVA", passing_score=50, max_attempts=3)
    q = Question.objects.create(test=test, question_text="Taux de TVA ?", points=1,
                                options=[{"text": "18 %", "is_correct": True}, {"text": "5 %", "is_correct": False}])
    return course, section, lesson, test, q


# --------------------------------------------------------------------------- #
# Building the course
# --------------------------------------------------------------------------- #
def test_saving_the_course_keeps_the_quiz(prof):
    """The course editor sends `test: null` for a quiz section edited elsewhere."""
    course, section, *_ = _course_with_quiz(prof)
    resp = _client(prof).put(f"{API}/courses/sections/{section.id}", {
        "title": "Quiz final", "order": 1, "content_type": "quiz", "test": None,
    }, format="json")
    assert resp.status_code == 200, resp.data
    assert CourseTest.objects.filter(section=section).exists()
    assert Question.objects.filter(test__section=section).count() == 1


def test_open_questions_are_accepted_and_left_out_of_the_score(prof, student):
    course, section, lesson, test, q = _course_with_quiz(prof, status=CourseStatus.PUBLISHED, is_free=True)
    resp = _client(prof).post(f"{API}/courses/tests/{test.id}/questions/", {
        "question_text": "Expliquez la TVA collectée.", "question_type": "essay", "options": [], "points": 5,
    }, format="json")
    assert resp.status_code == 201, resp.data

    Enrollment.objects.create(user=student, course=course)
    resp = _client(student).post(f"{API}/courses/{course.id}/tests/{test.id}/attempt", {
        "answers": [{"question_id": q.id, "answer": "18 %"}],
    }, format="json")
    attempt = resp.data["test_attempts"][-1]
    assert (attempt["score"], attempt["points_possible"]) == (100, 1)


def test_video_lessons_keep_their_url(prof):
    course = Course.objects.create(title="Vidéo", instructor=prof)
    section = CourseSection.objects.create(course=course, title="S", order=1)
    resp = _client(prof).post(f"{API}/courses/sections/{section.id}/lessons/", {
        "title": "Le bilan en vidéo", "type": "video", "video_url": "https://youtu.be/abc123", "order": 0,
    }, format="json")
    assert resp.status_code == 201
    assert CourseLesson.objects.get(pk=resp.data["id"]).video_url == "https://youtu.be/abc123"


# --------------------------------------------------------------------------- #
# Publishing
# --------------------------------------------------------------------------- #
def test_an_empty_course_cannot_be_published(prof):
    course = Course.objects.create(title="Vide", instructor=prof)
    client = _client(prof)
    assert client.post(f"{API}/courses/{course.id}/publish").status_code == 400
    assert client.patch(f"{API}/courses/{course.id}", {"status": "published"}, format="json").status_code == 400

    CourseSection.objects.create(course=course, title="S", order=1)
    CourseLesson.objects.create(section=course.sections.first(), title="L", type=LessonType.TEXT)
    assert client.post(f"{API}/courses/{course.id}/publish").status_code == 200


def test_no_certificate_for_an_empty_course(prof, student):
    course = Course.objects.create(title="Vide", instructor=prof, status=CourseStatus.PUBLISHED, is_free=True)
    Enrollment.objects.create(user=student, course=course)
    resp = _client(student).post(f"{API}/courses/{course.id}/me/check-certificate")
    assert resp.status_code == 400
    assert not Certificate.objects.exists()


def test_unpublishing_keeps_enrolled_students_in(prof, student):
    course, *_ = _course_with_quiz(prof, status=CourseStatus.PUBLISHED, is_free=True)
    Enrollment.objects.create(user=student, course=course)
    assert _client(prof).patch(f"{API}/courses/{course.id}", {"status": "draft"}, format="json").status_code == 200

    assert _client(student).get(f"{API}/courses/{course.id}").status_code == 200
    assert APIClient().get(f"{API}/courses/{course.id}").status_code == 404
    catalogue = APIClient().get(f"{API}/courses/").data
    rows = catalogue["results"] if isinstance(catalogue, dict) else catalogue  # paginated or not
    assert course.id not in [c["id"] for c in rows]


def test_public_course_page_hides_instructor_private_data(prof):
    course, *_ = _course_with_quiz(prof, status=CourseStatus.PUBLISHED, is_free=True)
    instructor = APIClient().get(f"{API}/courses/{course.id}").data["instructor"]
    assert instructor["name"] == "Aminata Diallo"
    assert instructor["professor_profile"]["specialization"] == "Comptabilité"
    assert not {"email", "phone", "birthdate"} & set(instructor)


# --------------------------------------------------------------------------- #
# Deleting
# --------------------------------------------------------------------------- #
def test_a_course_with_students_cannot_be_deleted(prof, student):
    course, *_ = _course_with_quiz(prof, status=CourseStatus.PUBLISHED, price=5000)
    Payment.objects.create(user=student, course=course, amount=5000, status=PaymentStatus.COMPLETED)
    Enrollment.objects.create(user=student, course=course)
    Certificate.objects.create(user=student, course=course, verification_code="CERT-KEEP00001")

    resp = _client(prof).delete(f"{API}/courses/{course.id}")
    assert resp.status_code == 409
    assert "brouillon" in resp.data["detail"]
    assert Course.objects.filter(pk=course.id).exists()
    assert Payment.objects.count() == 1 and Certificate.objects.count() == 1


def test_a_course_without_students_can_be_deleted(prof):
    course, *_ = _course_with_quiz(prof)
    assert _client(prof).delete(f"{API}/courses/{course.id}").status_code == 204


# --------------------------------------------------------------------------- #
# Following students
# --------------------------------------------------------------------------- #
def test_instructor_sees_students_progress_and_quiz_results(prof, student, roles):
    course, section, lesson, test, q = _course_with_quiz(prof, status=CourseStatus.PUBLISHED, price=5000)
    Payment.objects.create(user=student, course=course, amount=5000, status=PaymentStatus.COMPLETED)
    Enrollment.objects.create(user=student, course=course)
    s = _client(student)
    s.post(f"{API}/courses/{course.id}/lessons/{lesson.id}/complete")
    s.post(f"{API}/courses/{course.id}/tests/{test.id}/attempt", {"answers": [{"question_id": q.id, "answer": 1}]}, format="json")

    resp = _client(prof).get(f"{API}/courses/{course.id}/students")
    assert resp.status_code == 200
    [row] = resp.data
    assert row["name"] == "Awa Koné" and row["email"] == "eleve@acathecpa.test"
    assert row["progress_percentage"] == 50.0
    assert row["quizzes"] == [{"test_id": test.id, "title": "Quiz TVA", "attempts": 1, "best_score": 0, "passed": False}]
    assert row["certificate_code"] is None

    other_prof = _user("autre@acathecpa.test", roles["professor"])
    assert _client(other_prof).get(f"{API}/courses/{course.id}/students").status_code == 403
    assert s.get(f"{API}/courses/{course.id}/students").status_code == 403

    [mine] = _client(prof).get(f"{API}/courses/instructor/me").data
    assert (mine["students_count"], mine["revenue"]) == (1, 5000.0)


def test_dashboard_shows_real_numbers(prof, student, roles):
    course, *_ = _course_with_quiz(prof, status=CourseStatus.PUBLISHED, price=5000)
    other = _user("autre.eleve@acathecpa.test", roles["student"])
    Payment.objects.create(user=student, course=course, amount=5000, status=PaymentStatus.COMPLETED)
    Enrollment.objects.create(user=student, course=course, progress_percentage=100, completed_at=timezone.now())
    Enrollment.objects.create(user=other, course=course)
    Certificate.objects.create(user=student, course=course, verification_code="CERT-DASH00001")
    c = _client(prof)

    stats = c.get(f"{API}/professors/dashboard/stats").data
    assert stats["total_students_count"] == 2
    assert stats["certificates_count"] == 1 and stats["revenue"] == 5000.0
    assert c.get(f"{API}/professors/dashboard/student-distribution").data == {
        "active_students_count": 0, "inactive_students_count": 1, "completed_students_count": 1,
    }
    [engagement] = c.get(f"{API}/professors/dashboard/student-engagement").data
    assert engagement["average_progress"] == 50.0
    activities = c.get(f"{API}/professors/dashboard/recent-activities").data
    assert {a["activity_type"] for a in activities} == {"enrollment", "certificate"}


# --------------------------------------------------------------------------- #
# Profile and content
# --------------------------------------------------------------------------- #
def test_professor_edits_own_profile(prof):
    c = _client(prof)
    resp = c.put(f"{API}/professors/me/profile", {"bio": "20 ans d'audit", "skills": ["OHADA"]}, format="json")
    assert resp.status_code == 200
    assert c.get(f"{API}/professors/me/profile").data["bio"] == "20 ans d'audit"


def test_professor_can_write_an_article(prof):
    resp = _client(prof).post(f"{API}/contents/", {
        "title": "La TVA au Bénin", "type": "article", "content_body": "<p>…</p>",
    }, format="json")
    assert resp.status_code == 201, resp.data


# --------------------------------------------------------------------------- #
# Live sessions
# --------------------------------------------------------------------------- #
def test_live_session_needs_a_course_and_notifies_students(prof, student):
    course, *_ = _course_with_quiz(prof, status=CourseStatus.PUBLISHED, is_free=True)
    Enrollment.objects.create(user=student, course=course)
    c = _client(prof)
    when = (timezone.now() + timedelta(days=2)).isoformat()

    assert c.post(f"{API}/live-sessions/", {"title": "Sans cours", "scheduled_for": when}, format="json").status_code == 400

    resp = c.post(f"{API}/live-sessions/", {"title": "Q/R TVA", "scheduled_for": when, "course_id": course.id}, format="json")
    assert resp.status_code == 201
    [email] = mail.outbox
    assert email.bcc == ["eleve@acathecpa.test"] and "Q/R TVA" in email.subject

    later = (timezone.now() + timedelta(days=3)).isoformat()
    assert c.post(f"{API}/live-sessions/{resp.data['id']}/reschedule", {"scheduled_for": later}, format="json").status_code == 201
    assert "reprogrammée" in mail.outbox[-1].body


def _rsa_pair():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()
    return pem, key.public_key()


def test_each_participant_gets_own_jitsi_token(prof, student):
    pem, public_key = _rsa_pair()
    course, *_ = _course_with_quiz(prof, status=CourseStatus.PUBLISHED, is_free=True)
    Enrollment.objects.create(user=student, course=course)
    session = LiveSession.objects.create(course=course, host=prof, title="Direct",
                                         scheduled_for=timezone.now(), meeting_room_name="room-1")

    with override_settings(JITSI_APP_ID="vpaas-magic-cookie-1", JITSI_KID="vpaas-magic-cookie-1/abc",
                           JITSI_PRIVATE_KEY=pem, JITSI_JWT="static-shared-token"):
        host = _client(prof).post(f"{API}/live-sessions/{session.id}/join").data
        guest = _client(student).post(f"{API}/live-sessions/{session.id}/join").data

    def claims(token):
        assert jwt.get_unverified_header(token)["kid"] == "vpaas-magic-cookie-1/abc"
        return jwt.decode(token, public_key, algorithms=["RS256"], audience="jitsi")

    assert host["jwt"] != "static-shared-token"
    assert claims(host["jwt"])["context"]["user"]["moderator"] == "true"
    guest_claims = claims(guest["jwt"])
    assert guest_claims["context"]["user"] == {
        "id": str(student.id), "name": "Awa Koné", "email": "eleve@acathecpa.test", "moderator": "false",
    }
    assert guest_claims["room"] == "room-1"
