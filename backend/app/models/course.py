from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Text, Float, Boolean
from sqlalchemy.types import JSON # Ensure JSON is imported
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class CourseStatus(enum.Enum):
    draft = "draft"
    published = "published"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLAlchemyEnum(CourseStatus), default=CourseStatus.draft)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    price = Column(Float, nullable=True, default=0.0)
    is_free = Column(Boolean, default=False)
    short_description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    objectives = Column(JSON, nullable=True)
    prerequisites = Column(JSON, nullable=True)
    points_required_for_certificate = Column(Integer, nullable=True) # Added
    category = Column(String, nullable=True)
    level = Column(String, nullable=True)

    instructor = relationship("User", back_populates="instructed_courses")
    sections = relationship("CourseSection", back_populates="course", cascade="all, delete-orphan")
    live_sessions = relationship("LiveSession", back_populates="course")
    certificates = relationship("Certificate", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="course", cascade="all, delete-orphan")
    enrolled_students = relationship("User", secondary="enrollments", back_populates="enrolled_courses")

    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}')>"