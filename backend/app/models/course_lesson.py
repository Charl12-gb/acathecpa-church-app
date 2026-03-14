from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, Text, ForeignKey, Boolean, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from .user import Base 
import enum

class LessonType(enum.Enum):
    video = "video"
    text = "text"
    quiz = "quiz" # This might imply a link to a CourseTest or a simpler embedded quiz

class CourseLesson(Base):
    __tablename__ = "course_lessons"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("course_sections.id"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(SQLAlchemyEnum(LessonType), nullable=False)
    content_body = Column(Text, nullable=True) # Renamed from 'content'
    duration = Column(String, nullable=True) # E.g., "10:30" (10 mins 30 secs)
    order = Column(Integer, nullable=False, default=0) 
    is_completed = Column(Boolean, default=False, nullable=False) # Added
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    section = relationship("CourseSection", back_populates="lessons")

    def __repr__(self):
        return f"<CourseLesson(id={self.id}, title='{self.title}', type='{self.type.value}')>"
