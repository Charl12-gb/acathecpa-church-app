from pydantic import BaseModel
from typing import Optional
from app.models.course_lesson import LessonType

class CourseLessonBase(BaseModel):
    id: Optional[int] = None
    title: str
    order: int
    duration: Optional[str] = None # E.g., "10 minutes" or an integer for minutes
    content_body: Optional[str] = None # For text lessons, or URL for video/external content
    type: LessonType = LessonType.text
    is_completed: Optional[bool] = False

class CourseLessonCreate(CourseLessonBase):
    # section_id is typically a path parameter
    pass

class CourseLessonUpdate(CourseLessonBase):
    title: Optional[str] = None # All fields optional
    order: Optional[int] = None
    duration: Optional[str] = None
    content_body: Optional[str] = None
    type: Optional[LessonType] = None
    is_completed: Optional[bool] = None

class CourseLesson(CourseLessonBase):
    id: int
    section_id: int

    class Config:
        orm_mode = True
