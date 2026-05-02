from pydantic import BaseModel, ConfigDict, Field
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
    course_id: Optional[int] = None
    host_id: Optional[int] = None # Will be set from current user usually
    meeting_room_name: Optional[str] = None # Can be auto-generated

class LiveSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[LiveSessionStatus] = None
    meeting_room_name: Optional[str] = None

class LiveSessionStatusUpdate(BaseModel):
    status: LiveSessionStatus

class JitsiJoinResponse(BaseModel):
    app_id: str
    domain: str
    room: str
    url: str
    jwt: Optional[str] = None
    uid: int


class LiveSessionAttendanceMember(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    first_joined_at: Optional[datetime] = None
    last_joined_at: Optional[datetime] = None
    last_left_at: Optional[datetime] = None
    total_duration_seconds: int = 0
    join_count: int = 0
    is_present: bool = False


class LiveSessionAttendanceSummary(BaseModel):
    session_id: int
    title: str
    status: LiveSessionStatus
    scheduled_for: datetime
    planned_duration_minutes: Optional[int] = None
    actual_started_at: Optional[datetime] = None
    actual_ended_at: Optional[datetime] = None
    actual_duration_seconds: int = 0
    unique_attendees: int = 0
    present_count: int = 0
    expected_attendees: Optional[int] = None
    attendance_rate: Optional[float] = None
    attendees: List[LiveSessionAttendanceMember] = Field(default_factory=list)


class LiveSessionReschedule(BaseModel):
    scheduled_for: datetime
    duration_minutes: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


class LiveSession(LiveSessionBase):
    id: int
    course_id: Optional[int] = None
    host_id: int
    host: Optional[User] = None
    actual_started_at: Optional[datetime] = None
    actual_ended_at: Optional[datetime] = None
    meeting_room_name: Optional[str] = None
    # participants: List[User] = [] # If you need to show who is in the session

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
