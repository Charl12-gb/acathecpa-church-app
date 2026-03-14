from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base # Make sure this import is correct for your project structure
from datetime import datetime

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Assuming your user table is 'users'
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False) # Assuming your course table is 'courses'
    issue_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    certificate_url = Column(String, nullable=True) # Could be a path to a generated PDF or a verification page URL
    verification_code = Column(String, unique=True, index=True, nullable=True) # For external verification

    # Relationships
    user = relationship("User", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")

    __table_args__ = (UniqueConstraint('user_id', 'course_id', name='uq_user_course_certificate'),)

    def __repr__(self):
        return f"<Certificate(id={self.id}, user_id={self.user_id}, course_id={self.course_id})>"
