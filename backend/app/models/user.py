from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.content import Content
from app.models.live_session import LiveSession
from app.models.course import Course
from app.models.course_section import CourseSection
from app.models.course_lesson import CourseLesson
from .professor import ProfessorProfile # Import ProfessorProfile


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    country = Column(String, nullable=True)
    birthdate = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    authored_content = relationship("Content", back_populates="author")
    instructed_courses = relationship("Course", back_populates="instructor")
    hosted_live_sessions = relationship("LiveSession", back_populates="host")
    live_session_attendances = relationship("LiveSessionAttendance", back_populates="user", cascade="all, delete-orphan")
    role = relationship("Roles", back_populates="users")
    user_permissions = relationship("UserPermissions", back_populates="user")
    professor_profile = relationship("ProfessorProfile", back_populates="user", uselist=False)  # Add relationship
    certificates = relationship("Certificate", back_populates="user", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")

    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    enrolled_courses = relationship("Course", secondary="enrollments", back_populates="enrolled_students")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
