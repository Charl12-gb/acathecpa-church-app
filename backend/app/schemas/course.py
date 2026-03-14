from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.course_section import CourseSectionBase
from .user import User 
from app.models.course import CourseStatus

class CourseBase(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    is_free: Optional[bool] = False
    short_description: Optional[str] = None
    image_url: Optional[str] = None
    objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    category: Optional[str] = None
    status: Optional[CourseStatus] = CourseStatus.draft
    points_required_for_certificate: Optional[int] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    title: Optional[str] = None # All fields should be optional for update
    description: Optional[str] = None
    price: Optional[float] = None
    is_free: Optional[bool] = None
    short_description: Optional[str] = None
    image_url: Optional[str] = None
    objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    category: Optional[str] = None
    level : Optional[str] = None
    status: Optional[CourseStatus] = None
    points_required_for_certificate: Optional[int] = None

class Course(CourseBase):
    id: int
    instructor_id: int
    progress: Optional[float] = None
    instructor: User # Added back
    sections: List[CourseSectionBase] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True