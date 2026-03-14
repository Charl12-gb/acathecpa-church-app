from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base

class ProfessorProfile(Base):
    __tablename__ = "professor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    specialization = Column(String, index=True)
    bio = Column(Text)
    education = Column(JSON)
    experience = Column(JSON)
    skills = Column(JSON)
    social_links = Column(JSON)

    user = relationship("User", back_populates="professor_profile")
