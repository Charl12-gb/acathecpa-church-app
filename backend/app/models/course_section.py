from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from app.models.course_test import CourseTest


# Renamed Enum: ContentType -> CourseSectionType
class CourseSectionType(enum.Enum):
    TEXT = "text"
    VIDEO = "video"
    QUIZ = "quiz"

class CourseSection(Base):
    __tablename__ = "course_sections"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    order = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # Updated field to use the new enum name and a distinct SQL enum name
    content_type = Column(SQLAlchemyEnum(CourseSectionType, name='coursesectiontype'), default=CourseSectionType.TEXT, nullable=False)
    video_url = Column(String, nullable=True)
    text_content = Column(Text, nullable=True)

    course = relationship("Course", back_populates="sections")
    lessons = relationship("CourseLesson", back_populates="section", cascade="all, delete-orphan")

    test = relationship("CourseTest", back_populates="section", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CourseSection(id={self.id}, title='{self.title}', course_id={self.course_id})>"
