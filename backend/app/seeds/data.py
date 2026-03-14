import random
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.professor import ProfessorProfile
from app.models.course import Course, CourseStatus
from app.models.course_section import CourseSection, CourseSectionType
from app.models.course_lesson import CourseLesson, LessonType
from app.models.content import Content, ContentType, ContentFormat, ContentStatus
from app.models.enrollments import Enrollment
from app.permissions.models import Roles
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_role_id(db: Session, role_name: str):
    role = db.query(Roles).filter(Roles.name == role_name).first()
    return role.id if role else None

def seed_data(db: Session):
    print("🌱 Lancement du seed des données de test...")

    # 1. Rôles
    prof_role_id = get_role_id(db, "professor")
    student_role_id = get_role_id(db, "student")

    if not prof_role_id or not student_role_id:
        print("❌ Rôles non trouvés. Veuillez lancer le seed des rôles d'abord.")
        return

    # 2. Création de professeurs
    professors = []
    for i in range(1, 4):
        email = f"prof{i}@example.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                name=f"Professeur {i}",
                hashed_password=pwd_context.hash("password123"),
                role_id=prof_role_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Profil professeur
            profile = ProfessorProfile(
                user_id=user.id,
                specialization=random.choice(["Théologie", "Missiologie", "Leadership", "Éthique"]),
                bio=f"Ceci est la biographie du professeur {i}. Expert en son domaine avec des années d'expérience.",
                skills=["Enseignement", "Recherche", "Prédication"],
                social_links={
                    "linkedin": "https://linkedin.com",
                    "twitter": "https://twitter.com"
                }
            )
            db.add(profile)
            db.commit()
        professors.append(user)

    # 3. Création de cours
    categories = [
        'Leadership Chrétien',
        'Théologie & Doctrine',
        'Homilétique & Prédication',
        'Pastorale & Conseil',
        'Mission & Évangélisation',
        'Théologie Pratique',
        'Missiologie Contextuelle'
    ]
    levels = ["beginner", "intermediate", "advanced"]

    for i in range(1, 10):
        title = f"Cours de Test {i}"
        course = db.query(Course).filter(Course.title == title).first()
        if not course:
            course = Course(
                title=title,
                short_description=f"Description courte pour le cours {i}.",
                description=f"Ceci est une description détaillée du cours {i}. Il couvre de nombreux sujets importants.",
                instructor_id=random.choice(professors).id,
                status=CourseStatus.published,
                price=random.choice([0, 5000, 10000, 15000]),
                is_free=random.choice([True, False]),
                category=random.choice(categories),
                level=random.choice(levels),
                objectives=["Objectif 1", "Objectif 2", "Objectif 3"],
                prerequisites=["Prérequis 1", "Prérequis 2"],
                image_url=f"https://picsum.photos/seed/course{i}/400/200"
            )
            if course.is_free:
                course.price = 0
            db.add(course)
            db.commit()
            db.refresh(course)

            # Sections
            for j in range(1, 4):
                section = CourseSection(
                    course_id=course.id,
                    title=f"Section {j} : Les bases",
                    order=j,
                    content_type=CourseSectionType.TEXT,
                    text_content=f"Contenu de la section {j} pour le cours {i}."
                )
                db.add(section)
                db.commit()
                db.refresh(section)

                # Leçons
                for k in range(1, 4):
                    lesson = CourseLesson(
                        section_id=section.id,
                        title=f"Leçon {k} : Introduction",
                        type=LessonType.text,
                        content_body=f"Ceci est le contenu de la leçon {k} de la section {j}.",
                        order=k
                    )
                    db.add(lesson)
            db.commit()

    # 4. Création de contenus (articles et podcasts)
    for i in range(1, 6):
        # Article
        title = f"Article de Théologie {i}"
        if not db.query(Content).filter(Content.title == title).first():
            content = Content(
                title=title,
                description=f"Description de l'article {i}",
                content_body=f"<p>Ceci est le corps de l'article {i}. Il contient des informations précieuses sur la théologie.</p>",
                type=ContentType.article,
                format=ContentFormat.text,
                author_id=random.choice(professors).id,
                status=ContentStatus.published,
                tags=["Théologie", "Doctrine"],
                is_premium=random.choice([True, False]),
                price=500.0 if i > 3 else 0.0
            )
            db.add(content)

        # Podcast
        title = f"Podcast Missiologique {i}"
        if not db.query(Content).filter(Content.title == title).first():
            content = Content(
                title=title,
                description=f"Épisode de podcast {i}",
                content_body=f"Notes pour l'épisode de podcast {i}.",
                type=ContentType.podcast,
                format=ContentFormat.audio,
                media_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                author_id=random.choice(professors).id,
                status=ContentStatus.published,
                tags=["Mission", "Afrique"],
                is_premium=random.choice([True, False]),
                price=1000.0 if i > 4 else 0.0
            )
            db.add(content)

    # 5. Création d'un étudiant de test et inscriptions
    student_email = "student@example.com"
    student = db.query(User).filter(User.email == student_email).first()
    if not student:
        student = User(
            email=student_email,
            name="Étudiant de Test",
            hashed_password=pwd_context.hash("password123"),
            role_id=student_role_id,
            is_active=True
        )
        db.add(student)
        db.commit()
        db.refresh(student)

    # Inscriptions et progrès pour l'étudiant
    all_courses = db.query(Course).all()
    for i, course in enumerate(all_courses[:5]): # Inscrire l'étudiant aux 5 premiers cours
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == student.id,
            Enrollment.course_id == course.id
        ).first()

        if not enrollment:
            # Simuler des progrès variés
            progress = [100.0, 75.0, 50.0, 25.0, 0.0][i]

            # Récupérer quelques leçons pour les marquer comme complétées
            all_lesson_ids = [l.id for s in course.sections for l in s.lessons]
            num_completed = int(len(all_lesson_ids) * (progress / 100.0))
            completed_lessons = all_lesson_ids[:num_completed]

            enrollment = Enrollment(
                user_id=student.id,
                course_id=course.id,
                progress_percentage=progress,
                completed_lessons=completed_lessons,
                enrolled_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            if progress == 100.0:
                enrollment.completed_at = datetime.utcnow()
            db.add(enrollment)

    # 6. Activité hebdomadaire simulée
    # (Le service calcule l'activité basée sur CourseLesson.updated_at,
    # mais pour le seed on peut juste s'assurer que des leçons ont été "mises à jour" récemment)
    # En pratique, le seed ci-dessus ne met pas à jour CourseLesson.updated_at spécifiquement pour l'étudiant
    # car le modèle CourseLesson est partagé. Le service devra peut-être être ajusté pour utiliser une table de logs d'activité.

    db.commit()

    print("✅ Données de test seedées avec succès !")
