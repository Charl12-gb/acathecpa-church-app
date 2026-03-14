from pydantic import BaseModel
from typing import Optional, List
from app.models.course_section import CourseSectionType
from app.schemas.course_lesson import CourseLessonBase
from app.schemas.course_test import CourseTestBase
from app.schemas.course_test import CourseTestCreate, CourseTestUpdate

class CourseSectionBase(BaseModel):
    id: Optional[int] = None
    title: str
    order: int
    content_type: CourseSectionType = CourseSectionType.TEXT # Updated to CourseSectionType
    video_url: Optional[str] = None
    text_content: Optional[str] = None
    lessons: List[CourseLessonBase] = []

class CourseSectionCreate(CourseSectionBase):
    test: Optional[CourseTestCreate] = None

class CourseSectionUpdate(CourseSectionBase):
    title: Optional[str] = None
    order: Optional[int] = None
    content_type: Optional[CourseSectionType] = None 
    video_url: Optional[str] = None
    text_content: Optional[str] = None
    test: Optional[CourseTestUpdate] = None

class CourseSection(CourseSectionBase):
    id: int
    lessons: List[CourseLessonBase] = []
    test: Optional[CourseTestBase] = None

    class Config:
        orm_mode = True