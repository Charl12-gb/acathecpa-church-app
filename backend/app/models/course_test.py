from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CourseTest(Base):
    __tablename__ = "course_tests"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("course_sections.id"), nullable=True) 
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True) # Duration in minutes
    passing_score = Column(Integer, nullable=True) # e.g. 70 for 70%
    max_attempts = Column(Integer, nullable=True, default=1)

    # Relationship to section
    section = relationship("CourseSection", back_populates="test")
    # Relationship to questions
    questions = relationship("TestQuestion", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CourseTest(id={self.id}, title='{self.title}')>"
