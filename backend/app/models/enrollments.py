from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Enrollment(Base):
    __tablename__ = "enrollments"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True)

    enrolled_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Using default=[] ensures a new list is created for each instance if not provided
    completed_lessons = Column(JSON, nullable=False, default=lambda: []) # Store list of lesson IDs
    completed_sections = Column(JSON, nullable=False, default=lambda: []) # Store list of section IDs
    test_attempts = Column(JSON, nullable=False, default=lambda: [])
    # Example: [{"test_id": 1, "score": 80, "passed": True, "attempted_at": "timestamp"}]
    test_scores = Column(JSON, nullable=False, default=lambda: [])
    # Example: [{"test_id": 1, "score": 80}]

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment(user_id={self.user_id}, course_id={self.course_id}, progress={self.progress_percentage}%)>"