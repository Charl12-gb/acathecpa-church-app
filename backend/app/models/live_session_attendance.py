from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class LiveSessionAttendance(Base):
    __tablename__ = "live_session_attendances"
    __table_args__ = (
        UniqueConstraint("live_session_id", "user_id", name="uq_live_session_attendance_session_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    live_session_id = Column(Integer, ForeignKey("live_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    first_joined_at = Column(DateTime, nullable=True)
    last_joined_at = Column(DateTime, nullable=True)
    last_left_at = Column(DateTime, nullable=True)
    total_duration_seconds = Column(Integer, nullable=False, default=0)
    join_count = Column(Integer, nullable=False, default=0)
    is_present = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    live_session = relationship("LiveSession", back_populates="attendances")
    user = relationship("User", back_populates="live_session_attendances")
