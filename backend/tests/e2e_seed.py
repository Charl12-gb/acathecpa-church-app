"""
Rebuild the SQLite database used by the Playwright end-to-end tests.

    cd backend && ../appEnv/bin/python tests/e2e_seed.py

Creates the roles/permissions, a professor and one published paid course:
    Section 1 "Les bases"  : intro text + 2 text lessons
    Section 2 "Le bilan"   : 1 video lesson + quiz (2 questions, 1 + 2 points,
                             pass at 70 %, 2 attempts)
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


def main() -> None:
    db_path = Path(settings.DATABASES["default"]["NAME"])
    assert db_path.parent.name == ".e2e", "Refusing to reset a non-e2e database"
    db_path.parent.mkdir(exist_ok=True)
    db_path.unlink(missing_ok=True)

    call_command("migrate", verbosity=0)
    call_command("seed_permissions", verbosity=0)

    from apps.accounts.models import User
    from apps.courses.models import (
        Course, CourseLesson, CourseSection, CourseStatus, CourseTest, LessonType, TestQuestion,
    )
    from apps.permissions.models import Role

    prof = User(email="prof.e2e@acathecpa.test", name="Prof. Aminata Diallo",
                role=Role.objects.get(name="professor"))
    prof.set_password("Password123!")
    prof.save()

    course = Course.objects.create(
        title=E2E_COURSE_TITLE,
        short_description="Le plan comptable, les journaux et la lecture du bilan.",
        description="Formation d'initiation au système comptable OHADA.",
        instructor=prof,
        status=CourseStatus.PUBLISHED,
        is_free=False,
        price=15000,
        level="Débutant",
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
    print(f"e2e database ready: {db_path}")


if __name__ == "__main__":
    main()
