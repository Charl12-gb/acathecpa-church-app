"""
Seed the database with realistic demo data.

Port of FastAPI `app/seeds/data.py::seed_data`. Creates:
    - 3 professors (with profiles)
    - 9 published courses (each with 3 sections × 3 lessons)
    - 5 articles + 5 podcasts
    - 1 student enrolled in the first 5 courses with varying progression

Usage::

    python manage.py seed_demo_data
"""
from __future__ import annotations

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import ProfessorProfile, User
from apps.content.models import Content, ContentFormat, ContentStatus, ContentType
from apps.courses.models import (
    Course,
    CourseLesson,
    CourseSection,
    CourseSectionType,
    CourseStatus,
    LessonType,
)
from apps.enrollments.models import Enrollment
from apps.permissions.models import Role


CATEGORIES = [
    "Leadership Chrétien",
    "Théologie & Doctrine",
    "Homilétique & Prédication",
    "Pastorale & Conseil",
    "Mission & Évangélisation",
    "Théologie Pratique",
    "Missiologie Contextuelle",
]
LEVELS = ["beginner", "intermediate", "advanced"]
SPECIALIZATIONS = ["Théologie", "Missiologie", "Leadership", "Éthique"]


class Command(BaseCommand):
    help = "Seed the database with demo professors, courses, content and an enrolled student."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo data..."))

        prof_role = Role.objects.filter(name="professor").first()
        student_role = Role.objects.filter(name="student").first()
        if not prof_role or not student_role:
            self.stderr.write(self.style.ERROR(
                "Roles missing — run `python manage.py seed_permissions` first."
            ))
            return

        professors = self._seed_professors(prof_role)
        self._seed_courses(professors)
        self._seed_content(professors)
        self._seed_student_with_enrollments(student_role)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    # ------------------------------------------------------------------ #
    def _seed_professors(self, role) -> list[User]:
        professors: list[User] = []
        for i in range(1, 4):
            email = f"prof{i}@example.com"
            user = User.objects.filter(email=email).first()
            if not user:
                user = User(email=email, name=f"Professeur {i}", role=role, is_active=True)
                user.set_password("password123")
                user.save()
                ProfessorProfile.objects.create(
                    user=user,
                    specialization=random.choice(SPECIALIZATIONS),
                    bio=(
                        f"Ceci est la biographie du professeur {i}. "
                        "Expert en son domaine avec des années d'expérience."
                    ),
                    skills=["Enseignement", "Recherche", "Prédication"],
                    social_links={
                        "linkedin": "https://linkedin.com",
                        "twitter": "https://twitter.com",
                    },
                )
                self.stdout.write(f"  + Created professor {email}")
            professors.append(user)
        return professors

    # ------------------------------------------------------------------ #
    def _seed_courses(self, professors: list[User]) -> None:
        for i in range(1, 10):
            title = f"Cours de Test {i}"
            if Course.objects.filter(title=title).exists():
                continue

            is_free = random.choice([True, False])
            course = Course.objects.create(
                title=title,
                short_description=f"Description courte pour le cours {i}.",
                description=(
                    f"Ceci est une description détaillée du cours {i}. "
                    "Il couvre de nombreux sujets importants."
                ),
                instructor=random.choice(professors),
                status=CourseStatus.PUBLISHED,
                price=0 if is_free else random.choice([5000, 10000, 15000]),
                is_free=is_free,
                category=random.choice(CATEGORIES),
                level=random.choice(LEVELS),
                objectives=["Objectif 1", "Objectif 2", "Objectif 3"],
                prerequisites=["Prérequis 1", "Prérequis 2"],
                image_url=f"https://picsum.photos/seed/course{i}/400/200",
            )

            for j in range(1, 4):
                section = CourseSection.objects.create(
                    course=course,
                    title=f"Section {j} : Les bases",
                    order=j,
                    content_type=CourseSectionType.TEXT,
                    text_content=f"Contenu de la section {j} pour le cours {i}.",
                )
                for k in range(1, 4):
                    CourseLesson.objects.create(
                        section=section,
                        title=f"Leçon {k} : Introduction",
                        type=LessonType.TEXT,
                        content_body=(
                            f"Ceci est le contenu de la leçon {k} de la section {j}."
                        ),
                        order=k,
                    )
            self.stdout.write(f"  + Created course '{title}' (3 sections × 3 lessons)")

    # ------------------------------------------------------------------ #
    def _seed_content(self, professors: list[User]) -> None:
        # Indices premium (1-based) — le reste est gratuit
        premium_articles = {4: 1500.0, 5: 2500.0}
        premium_podcasts = {3: 2000.0, 5: 3500.0}

        for i in range(1, 6):
            article_title = f"Article de Théologie {i}"
            article_premium = i in premium_articles
            article_price = premium_articles.get(i, 0.0)
            if not Content.objects.filter(title=article_title).exists():
                Content.objects.create(
                    title=article_title,
                    description=(
                        f"Description de l'article {i}"
                        + (" — contenu premium" if article_premium else "")
                    ),
                    content_body=(
                        f"<p>Ceci est le corps de l'article {i}. "
                        "Il contient des informations précieuses sur la théologie.</p>"
                    ),
                    type=ContentType.ARTICLE,
                    format=ContentFormat.TEXT,
                    author=random.choice(professors),
                    status=ContentStatus.PUBLISHED,
                    tags=["Théologie", "Doctrine"]
                    + (["Premium"] if article_premium else []),
                    is_premium=article_premium,
                    price=article_price,
                )

            podcast_title = f"Podcast Missiologique {i}"
            podcast_premium = i in premium_podcasts
            podcast_price = premium_podcasts.get(i, 0.0)
            if not Content.objects.filter(title=podcast_title).exists():
                Content.objects.create(
                    title=podcast_title,
                    description=(
                        f"Épisode de podcast {i}"
                        + (" — contenu premium" if podcast_premium else "")
                    ),
                    content_body=f"Notes pour l'épisode de podcast {i}.",
                    type=ContentType.PODCAST,
                    format=ContentFormat.AUDIO,
                    media_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                    author=random.choice(professors),
                    status=ContentStatus.PUBLISHED,
                    tags=["Mission", "Afrique"]
                    + (["Premium"] if podcast_premium else []),
                    is_premium=podcast_premium,
                    price=podcast_price,
                )
        self.stdout.write(
            "  + Created 5 articles (2 premium) + 5 podcasts (2 premium)"
        )

    # ------------------------------------------------------------------ #
    def _seed_student_with_enrollments(self, role) -> None:
        email = "student@example.com"
        student = User.objects.filter(email=email).first()
        if not student:
            student = User(
                email=email, name="Étudiant de Test", role=role, is_active=True
            )
            student.set_password("password123")
            student.save()
            self.stdout.write(f"  + Created student {email}")

        progressions = [100.0, 75.0, 50.0, 25.0, 0.0]
        for i, course in enumerate(Course.objects.all()[:5]):
            if Enrollment.objects.filter(user=student, course=course).exists():
                continue
            progress = progressions[i]
            lesson_ids = list(
                CourseLesson.objects.filter(section__course=course).values_list("id", flat=True)
            )
            num_done = int(len(lesson_ids) * (progress / 100.0))
            completed = lesson_ids[:num_done]
            enrollment = Enrollment.objects.create(
                user=student,
                course=course,
                progress_percentage=progress,
                completed_lessons=completed,
            )
            # Backdate
            backdated = timezone.now() - timedelta(days=random.randint(1, 30))
            Enrollment.objects.filter(pk=enrollment.pk).update(enrolled_at=backdated)
            if progress == 100.0:
                enrollment.completed_at = timezone.now()
                enrollment.save(update_fields=["completed_at"])
        self.stdout.write("  + Enrolled student in first 5 courses with varied progress")
