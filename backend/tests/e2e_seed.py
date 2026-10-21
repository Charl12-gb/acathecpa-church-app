"""
Rebuild the SQLite database used by the Playwright end-to-end tests.

    cd backend && ../appEnv/bin/python tests/e2e_seed.py

Creates the roles/permissions, a professor and:
    - "Comptabilité OHADA - Les fondamentaux" (published, 15 000 XOF), used by the
      student journey:
        Section 1 "Les bases" : intro text + 2 text lessons
        Section 2 "Le bilan"  : 1 lesson + quiz (2 questions, 1 + 2 points,
                                pass at 70 %, 2 attempts)
    - "Fiscalité des entreprises" (published, free) with one enrolled student
      halfway through, used by the professor journey;
    - "Brouillon vide" (draft, no content);
    - an admin, a super admin and a student without any history.
"""
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_e2e")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.core.management import call_command  # noqa: E402

E2E_COURSE_TITLE = "Comptabilité OHADA - Les fondamentaux"
E2E_PROF_COURSE_TITLE = "Fiscalité des entreprises"


def main() -> None:
    db_path = Path(settings.DATABASES["default"]["NAME"])
    assert db_path.parent.name == ".e2e", "Refusing to reset a non-e2e database"
    db_path.parent.mkdir(exist_ok=True)
    db_path.unlink(missing_ok=True)

    call_command("migrate", verbosity=0)
    call_command("seed_permissions", verbosity=0)

    from apps.accounts.models import ProfessorProfile, User
    from apps.courses.models import (
        Category, Course, CourseLesson, CourseSection, CourseStatus, CourseTest, LessonType, TestQuestion,
    )
    from apps.enrollments.models import Enrollment
    from apps.permissions.models import Role

    prof = User(email="prof.e2e@acathecpa.test", name="Prof. Aminata Diallo",
                role=Role.objects.get(name="professor"))
    prof.set_password("Password123!")
    prof.save()
    ProfessorProfile.objects.create(user=prof, specialization="Comptabilité et fiscalité")
    Category.objects.create(name="Comptabilité")

    course = Course.objects.create(
        title=E2E_COURSE_TITLE,
        short_description="Le plan comptable, les journaux et la lecture du bilan.",
        description="Formation d'initiation au système comptable OHADA.",
        instructor=prof,
        status=CourseStatus.PUBLISHED,
        is_free=False,
        price=15000,
        level="Débutant",
        category="Comptabilité",
        points_required_for_certificate=2,
    )
    s1 = CourseSection.objects.create(
        course=course, title="Les bases", order=1, content_type="text",
        text_content="<p>Cette section présente l'organisation de la comptabilité.</p>",
    )
    CourseLesson.objects.create(section=s1, title="Le plan comptable", type=LessonType.TEXT, order=1,
                                content_body="<p>Le plan comptable OHADA compte 9 classes.</p>")
    CourseLesson.objects.create(section=s1, title="Les journaux", type=LessonType.TEXT, order=2,
                                content_body="<p>Toute opération est d'abord inscrite au journal.</p>")
    s2 = CourseSection.objects.create(course=course, title="Le bilan", order=2, content_type="quiz")
    CourseLesson.objects.create(section=s2, title="Lire un bilan", type=LessonType.TEXT, order=1,
                                content_body="<p>L'actif est à gauche, le passif à droite.</p>")
    test = CourseTest.objects.create(section=s2, title="Quiz : le bilan", passing_score=70, max_attempts=2)
    TestQuestion.objects.create(test=test, question_text="De quel côté du bilan se trouve l'actif ?", points=1,
                                options=[{"text": "À gauche", "is_correct": True},
                                         {"text": "À droite", "is_correct": False}])
    TestQuestion.objects.create(test=test, question_text="Le capital social fait partie de l'actif.", points=2,
                                options=[{"text": "Vrai", "is_correct": False},
                                         {"text": "Faux", "is_correct": True}])

    fisc = Course.objects.create(
        title=E2E_PROF_COURSE_TITLE, short_description="TVA, IS et obligations déclaratives.",
        instructor=prof, status=CourseStatus.PUBLISHED, is_free=True, price=0, category="Comptabilité",
    )
    fs1 = CourseSection.objects.create(course=fisc, title="La TVA", order=1, content_type="quiz")
    tva = CourseLesson.objects.create(section=fs1, title="Principes de la TVA", type=LessonType.TEXT, order=1,
                                      content_body="<p>La TVA est un impôt sur la consommation.</p>")
    CourseLesson.objects.create(section=fs1, title="Taux applicables", type=LessonType.TEXT, order=2,
                                content_body="<p>Taux normal : 18 %.</p>")
    fq = CourseTest.objects.create(section=fs1, title="Quiz TVA", passing_score=50, max_attempts=3)
    TestQuestion.objects.create(test=fq, question_text="Taux normal de TVA ?", points=1,
                                options=[{"text": "18 %", "is_correct": True}, {"text": "5 %", "is_correct": False}])
    koffi = User(email="koffi.e2e@acathecpa.test", name="Koffi Mensah", role=Role.objects.get(name="student"))
    koffi.set_password("Password123!")
    koffi.save()
    Enrollment.objects.create(
        user=koffi, course=fisc, completed_lessons=[tva.id], progress_percentage=33.3,
        test_attempts=[{"test_id": fq.id, "attempt_number": 1, "score": 0.0, "passed": False,
                        "points_earned": 0, "points_possible": 1, "attempted_at": "2026-10-16T10:00:00+00:00",
                        "questions_summary": []}],
    )

    Course.objects.create(title="Brouillon vide", instructor=prof, status=CourseStatus.DRAFT,
                          is_free=True, price=0, category="Comptabilité")

    # An article the professor edits (content editor journey).
    from apps.content.models import Content

    Content.objects.create(
        title="Les obligations fiscales", type="article", format="text", status="published",
        description="Calendrier des déclarations.", author=prof,
        content_body="<p>Chaque entreprise déclare sa TVA chaque mois.</p>",
    )
    # A draft by another author, moderated then deleted by an admin.
    autre = User(email="autre.prof.e2e@acathecpa.test", name="Prof. Kossi Agbo", role=Role.objects.get(name="professor"))
    autre.set_password("Password123!")
    autre.save()
    Content.objects.create(title="Brouillon à modérer", type="podcast", format="text", status="draft",
                           author=autre, content_body="<p>Épisode en préparation.</p>")

    # A paying student of the OHADA course, deleted for good by the super admin.
    from apps.payments.models import Payment, PaymentStatus

    yao = User(email="yao.e2e@acathecpa.test", name="Yao Adjo", role=Role.objects.get(name="student"))
    yao.set_password("Password123!")
    yao.save()
    Payment.objects.create(user=yao, course=course, amount=15000, status=PaymentStatus.COMPLETED,
                           transaction_ref="TXN-E2E-YAO")
    Enrollment.objects.create(user=yao, course=course)

    # Back-office accounts and a student with no history (admin journey).
    for email, name, role in [
        ("admin.e2e@acathecpa.test", "Admin Plateforme", "admin"),
        ("super.e2e@acathecpa.test", "Super Admin", "super_admin"),
        ("nouveau.e2e@acathecpa.test", "Nouvel Inscrit", "student"),
    ]:
        u = User(email=email, name=name, role=Role.objects.get(name=role))
        u.set_password("Password123!")
        u.save()
    print(f"e2e database ready: {db_path}")


if __name__ == "__main__":
    main()
