from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.live_session import LiveSessionStatus
from .user import User # For host representation

class LiveSessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_for: datetime
    duration_minutes: Optional[int] = None
    status: LiveSessionStatus = LiveSessionStatus.scheduled

class LiveSessionCreate(LiveSessionBase):
    course_id: int
    host_id: Optional[int] = None # Will be set from current user usually
    agora_channel_name: Optional[str] = None # Can be auto-generated

class LiveSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[LiveSessionStatus] = None
    agora_channel_name: Optional[str] = None

class LiveSession(LiveSessionBase):
    id: int
    course_id: int
    host_id: int
    host: Optional[User] = None
    agora_channel_name: Optional[str] = None
    # participants: List[User] = [] # If you need to show who is in the session

    class Config:
        orm_mode = True
        use_enum_values = True
