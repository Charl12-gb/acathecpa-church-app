# Puis importer les modèles
from .user import User
from .course import Course
from .professor import ProfessorProfile # Import ProfessorProfile
from .certificate import Certificate

# Assurer que tous les modèles sont disponibles
__all__ = ["User", "Course", "enrollments", "ProfessorProfile", "Certificate"] # Add ProfessorProfile to __all__
