from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class LiveSessionStatus(enum.Enum):
    scheduled = "scheduled"
    live = "live"
    ended = "ended"

# Association table for LiveSession participants (many-to-many with User)
# live_session_participants = Table('live_session_participants', Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
#     Column('live_session_id', Integer, ForeignKey('live_sessions.id'), primary_key=True)
# )
# The 'participants' array in the store seems to be dynamic based on who joins.
# For persistent tracking, a table like above would be needed. For now, assume it's managed by Agora/app logic.

class LiveSession(Base):
    __tablename__ = "live_sessions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    scheduled_for = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=True) # Duration in minutes
    host_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLAlchemyEnum(LiveSessionStatus), default=LiveSessionStatus.scheduled)
    
    # Fields for Agora integration if needed persistently
    agora_channel_name = Column(String, nullable=True, unique=True) # Channel name should be unique
    # agora_token = Column(String, nullable=True) # Tokens are often short-lived and generated on demand

    course = relationship("Course", back_populates="live_sessions")
    host = relationship("User", back_populates="hosted_live_sessions")
    # participants = relationship("User", secondary=live_session_participants, back_populates="attended_live_sessions")


    def __repr__(self):
        return f"<LiveSession(id={self.id}, title='{self.title}', status='{self.status.value}')>"
