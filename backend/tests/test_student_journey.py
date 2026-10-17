"""
End-to-end student journey, through the HTTP API with the real seeded roles:

    sign-up -> login -> browse -> (simulated) payment -> enrollment
    -> lessons -> quiz -> certificate -> public verification

plus the guards added around each step.
"""
from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.courses.models import (
    Course,
    CourseLesson,
    CourseSection,
    CourseStatus,
    CourseTest,
    LessonType,
    TestQuestion as Question,
)
from apps.live_sessions.models import LiveSession
from apps.permissions.models import Role

API = "/api/v1"


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def roles(db):
    call_command("seed_permissions", verbosity=0)
    return {r.name: r for r in Role.objects.all()}


def _user(email, role, password="Password123!"):
    user = User(email=email, name=email.split("@")[0].title(), role=role)
    user.set_password(password)
    user.save()
    return user


def _client(user=None):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user)
    return client


@pytest.fixture
def professor(roles):
    return _user("prof@acathecpa.test", roles["professor"])


@pytest.fixture
def paid_course(professor):
    """
    Paid course, two sections:
        S1: two text lessons
        S2: one video lesson + a quiz (2 questions, 1 + 2 points, pass at 70 %,
            2 attempts max)
    Certificate requires 2 quiz points.
    """
    course = Course.objects.create(
        title="Comptabilité OHADA",
        instructor=professor,
        status=CourseStatus.PUBLISHED,
        is_free=False,
        price=15000.0,
        points_required_for_certificate=2,
    )
    s1 = CourseSection.objects.create(course=course, title="Bases", order=1)
    s2 = CourseSection.objects.create(course=course, title="Bilan", order=2)
    lessons = [
        CourseLesson.objects.create(section=s1, title="Le plan comptable", type=LessonType.TEXT,
                                    content_body="<p>Classes 1 à 9</p>", order=1),
        CourseLesson.objects.create(section=s1, title="Les journaux", type=LessonType.TEXT,
                                    content_body="<p>Journal général</p>", order=2),
        CourseLesson.objects.create(section=s2, title="Lire un bilan", type=LessonType.VIDEO,
                                    video_url="https://video.test/bilan", order=1),
    ]
    test = CourseTest.objects.create(section=s2, title="Quiz bilan", passing_score=70, max_attempts=2)
    q1 = Question.objects.create(
        test=test, question_text="L'actif est à…", points=1,
        options=[{"text": "gauche", "is_correct": True}, {"text": "droite", "is_correct": False}],
    )
    q2 = Question.objects.create(
        test=test, question_text="Le capital est un…", points=2,
        options=[{"text": "Vrai", "is_correct": False}, {"text": "Faux", "is_correct": True}],
    )
    return {"course": course, "sections": [s1, s2], "lessons": lessons, "test": test, "questions": [q1, q2]}


# --------------------------------------------------------------------------- #
# The full journey
# --------------------------------------------------------------------------- #
def test_full_student_journey(roles, paid_course):
    course = paid_course["course"]
    s1, s2 = paid_course["sections"]
    l1, l2, l3 = paid_course["lessons"]
    test = paid_course["test"]
    q1, q2 = paid_course["questions"]
    anon = APIClient()

    # 1. Sign-up: a role sent by the public form is ignored.
    resp = anon.post(f"{API}/auth/register", {
        "email": "awa@acathecpa.test", "name": "Awa Koné",
        "password": "Password123!", "role_name": "super_admin",
    }, format="json")
    assert resp.status_code == 201, resp.data
    awa = User.objects.get(email="awa@acathecpa.test")
    assert awa.role.name == "student"

    # 2. Login
    resp = anon.post(f"{API}/auth/login", {"username": "awa@acathecpa.test", "password": "Password123!"})
    assert resp.status_code == 200
    student = APIClient()
    student.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access_token']}")

    # 3. Browsing: the public page shows the outline only.
    resp = anon.get(f"{API}/courses/{course.id}")
    assert resp.status_code == 200
    section1 = resp.data["sections"][0]
    assert [l["title"] for l in section1["lessons"]] == ["Le plan comptable", "Les journaux"]
    assert "content_body" not in section1["lessons"][0]
    quiz = resp.data["sections"][1]["test"]
    assert "questions" not in quiz and quiz["question_count"] == 2

    # Not enrolled yet: no lesson content.
    assert student.get(f"{API}/courses/lessons/{l1.id}").status_code == 403

    # 4. Paid course: enrollment needs a payment.
    assert student.post(f"{API}/courses/{course.id}/enroll").status_code == 402

    resp = student.post(f"{API}/payments/", {"course_id": course.id, "amount": 1}, format="json")
    assert resp.status_code == 201
    assert resp.data["amount"] == 15000.0  # server price, not the client amount
    assert resp.data["status"] == "pending"
    payment_id = resp.data["id"]

    resp = student.post(f"{API}/payments/{payment_id}/confirm")
    assert resp.status_code == 200 and resp.data["status"] == "completed"

    resp = student.post(f"{API}/courses/{course.id}/enroll")
    assert resp.status_code == 201

    # 5. Enrolled: lesson content is visible, quiz answers are not.
    resp = student.get(f"{API}/courses/{course.id}")
    assert resp.data["sections"][0]["lessons"][0]["content_body"] == "<p>Classes 1 à 9</p>"
    questions = resp.data["sections"][1]["test"]["questions"]
    assert questions[0]["options"] == [{"text": "gauche"}, {"text": "droite"}]
    assert "correct_answer_data" not in questions[0]
    resp = student.get(f"{API}/courses/tests/{test.id}")
    assert all("is_correct" not in o for q in resp.data["questions"] for o in q["options"])

    # 6. Lessons
    for lesson in (l1, l2):
        assert student.post(f"{API}/courses/{course.id}/lessons/{lesson.id}/complete").status_code == 200
    resp = student.get(f"{API}/courses/{course.id}/me/progress")
    assert s1.id in resp.data["completed_sections"]
    resp = student.post(f"{API}/courses/{course.id}/lessons/{l3.id}/complete")
    assert resp.status_code == 200
    assert resp.data["progress_percentage"] == 75.0  # 3 lessons done, quiz not passed

    # Section 2 is not done until its quiz is passed; no certificate yet.
    assert student.post(f"{API}/courses/{course.id}/sections/{s2.id}/complete").status_code == 400
    assert student.post(f"{API}/courses/{course.id}/me/check-certificate").status_code == 400

    # 7. Quiz: graded on the server.
    attempt_url = f"{API}/courses/{course.id}/tests/{test.id}/attempt"
    wrong = {"answers": [{"question_id": q1.id, "answer": "droite"}, {"question_id": q2.id, "answer": "Vrai"}]}
    resp = student.post(attempt_url, wrong, format="json")
    assert resp.status_code == 200
    last = resp.data["test_attempts"][-1]
    assert (last["score"], last["passed"], last["attempt_number"]) == (0, False, 1)

    right = {"answers": [{"question_id": q1.id, "answer": "gauche"}, {"question_id": q2.id, "answer": 1}]}
    resp = student.post(attempt_url, right, format="json")
    last = resp.data["test_attempts"][-1]
    assert (last["score"], last["passed"], last["points_earned"]) == (100, True, 3)
    assert s2.id in resp.data["completed_sections"]
    assert resp.data["progress_percentage"] == 100.0

    # max_attempts = 2
    resp = student.post(attempt_url, right, format="json")
    assert resp.status_code == 400

    # 8. Certificate
    resp = student.post(f"{API}/courses/{course.id}/me/check-certificate")
    assert resp.status_code == 201, resp.data
    code = resp.data["verification_code"]
    assert resp.data["certificate_url"] == f"/certificates/verify/{code}"

    resp = student.get(f"{API}/courses/{course.id}/certificate")
    assert resp.status_code == 200 and resp.data["verification_code"] == code
    assert len(student.get(f"{API}/courses/me/certificates").data) == 1

    # 9. Anyone can verify the certificate.
    resp = anon.get(f"{API}/certificates/verify/{code}")
    assert resp.status_code == 200
    assert resp.data["holder_name"] == "Awa Koné"
    assert resp.data["course_title"] == "Comptabilité OHADA"
    assert anon.get(f"{API}/certificates/verify/CERT-INCONNU").status_code == 404


# --------------------------------------------------------------------------- #
# Guards
# --------------------------------------------------------------------------- #
def test_admin_can_still_create_a_professor(roles):
    admin = _user("admin@acathecpa.test", roles["admin"])
    resp = _client(admin).post(f"{API}/auth/register", {
        "email": "newprof@acathecpa.test", "password": "Password123!", "role": "professor",
    }, format="json")
    assert resp.status_code == 201
    assert User.objects.get(email="newprof@acathecpa.test").role.name == "professor"


def test_simulated_payment_can_fail(roles, paid_course):
    student = _client(_user("eleve@acathecpa.test", roles["student"]))
    course = paid_course["course"]
    pid = student.post(f"{API}/payments/", {"course_id": course.id}, format="json").data["id"]
    resp = student.post(f"{API}/payments/{pid}/confirm", {"simulate": "failure"}, format="json")
    assert resp.data["status"] == "failed"
    assert student.post(f"{API}/courses/{course.id}/enroll").status_code == 402


@override_settings(PAYMENT_PROVIDER="fedapay")
def test_self_confirmation_disabled_outside_simulation(roles, paid_course):
    student = _client(_user("eleve@acathecpa.test", roles["student"]))
    pid = student.post(f"{API}/payments/", {"course_id": paid_course["course"].id}, format="json").data["id"]
    assert student.post(f"{API}/payments/{pid}/confirm").status_code == 403


def test_draft_course_hidden_from_public(professor):
    draft = Course.objects.create(title="Brouillon", instructor=professor, status=CourseStatus.DRAFT)
    assert APIClient().get(f"{API}/courses/{draft.id}").status_code == 404
    assert _client(professor).get(f"{API}/courses/{draft.id}").status_code == 200


def test_professor_still_sees_quiz_answers(paid_course, professor):
    resp = _client(professor).get(f"{API}/courses/tests/{paid_course['test'].id}")
    assert resp.data["questions"][0]["options"][0]["is_correct"] is True


def test_cannot_complete_lesson_from_another_course(roles, paid_course, professor):
    student_user = _user("eleve@acathecpa.test", roles["student"])
    student = _client(student_user)
    free = Course.objects.create(title="Gratuit", instructor=professor,
                                 status=CourseStatus.PUBLISHED, is_free=True)
    assert student.post(f"{API}/courses/{free.id}/enroll").status_code == 201
    foreign_lesson = paid_course["lessons"][0]
    resp = student.post(f"{API}/courses/{free.id}/lessons/{foreign_lesson.id}/complete")
    assert resp.status_code == 404


@override_settings(JITSI_APP_ID="vpaas-test")
def test_live_sessions_reserved_to_enrolled_students(roles, professor):
    course = Course.objects.create(title="Fiscalité", instructor=professor,
                                   status=CourseStatus.PUBLISHED, is_free=True)
    session = LiveSession.objects.create(
        course=course, host=professor, title="Questions/réponses",
        scheduled_for=timezone.now() + timedelta(days=1),
    )
    enrolled = _client(_user("inscrit@acathecpa.test", roles["student"]))
    outsider = _client(_user("autre@acathecpa.test", roles["student"]))
    enrolled.post(f"{API}/courses/{course.id}/enroll")

    resp = enrolled.get(f"{API}/live-sessions/")
    assert [s["id"] for s in resp.data] == [session.id]
    assert outsider.get(f"{API}/live-sessions/").data == []

    assert enrolled.post(f"{API}/live-sessions/{session.id}/join").status_code == 200
    assert outsider.post(f"{API}/live-sessions/{session.id}/join").status_code == 403


def test_several_students_can_sign_up_without_phone(roles):
    # The sign-up form sends phone="" when the field is left empty.
    for email in ("a@acathecpa.test", "b@acathecpa.test"):
        resp = APIClient().post(f"{API}/auth/register", {
            "email": email, "name": "Sans Téléphone", "phone": "", "password": "Password123!",
        }, format="json")
        assert resp.status_code == 201, resp.data
    assert User.objects.filter(phone__isnull=True).count() == 2
