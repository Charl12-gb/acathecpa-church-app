from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context

# Importation de l'engine et des modèles
from app.database import engine, Base
from app.models import *
from app.permissions.models import *  
from app.models.professor import ProfessorProfile
from app.models.course import Course
from app.models.course_section import CourseSection
from app.models.course_section import CourseSectionType
from app.models.course_lesson import CourseLesson
from app.models.course_test import CourseTest
from app.models.test_question import TestQuestion, QuestionType
from app.models.enrollments import Enrollment

# Accès à la configuration Alembic
config = context.config

# Configuration du logging si un fichier de configuration existe
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Utilisation des métadonnées pour autogénérer les migrations
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Exécuter les migrations en mode 'offline'.
    Dans ce mode, Alembic utilise juste l'URL de la base de données sans établir
    de connexion avec celle-ci.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Exécuter les migrations en mode 'online'.
    Dans ce mode, Alembic se connecte à la base de données en utilisant l'engine.
    """
    # Utilisation de l'engine déjà défini dans app.database
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Détecter si on est en mode 'offline' ou 'online' et exécuter les migrations
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
