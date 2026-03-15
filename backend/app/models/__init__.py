# Importer tous les modèles dans le bon ordre pour que SQLAlchemy
# puisse résoudre toutes les relationships déclarées par string.
from .content import Content
from .live_session import LiveSession
from .course_section import CourseSection
from .course_lesson import CourseLesson
from .course_test import CourseTest
from .test_question import TestQuestion
from .professor import ProfessorProfile
from .course import Course
from .enrollments import Enrollment
from .certificate import Certificate
from .payment import Payment
from .user import User

# Modèles de permissions
from app.permissions.models import Roles, Permissions, RolesPermissions, UserPermissions

__all__ = [
    "Content",
    "LiveSession",
    "CourseSection",
    "CourseLesson",
    "CourseTest",
    "TestQuestion",
    "ProfessorProfile",
    "Course",
    "Enrollment",
    "Certificate",
    "Payment",
    "User",
    "Roles",
    "Permissions",
    "RolesPermissions",
    "UserPermissions",
]
