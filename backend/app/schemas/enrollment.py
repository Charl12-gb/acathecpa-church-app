from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class TestAttemptQuestionSummary(BaseModel):
    question_id: int
    # Add other relevant fields from your TestQuestion model or how you store answers, e.g.:
    # answer_provided: Optional[Any] = None
    is_correct: Optional[bool] = None
    points_earned: Optional[float] = None

class TestAttemptSchema(BaseModel):
    test_id: int
    score: float
    passed: bool
    attempted_at: datetime # Changed from isoformat string to datetime for consistency
    questions_summary: Optional[List[TestAttemptQuestionSummary]] = None

class TestScoreSchema(BaseModel):
    test_id: int
    score: float
    # Optional: Add points_awarded if it's distinct from score and relevant here
    # points_awarded: Optional[float] = None

class EnrollmentBase(BaseModel):
    user_id: int
    course_id: int
    enrolled_at: datetime
    progress_percentage: float
    completed_at: Optional[datetime] = None

class EnrollmentProgress(EnrollmentBase):
    completed_lessons: List[int]
    completed_sections: List[int]
    test_attempts: List[TestAttemptSchema]
    test_scores: List[TestScoreSchema]

    class Config:
        orm_mode = True # Kept for potential direct model usage

class EnrollmentCreate(BaseModel): # Not strictly needed for this task but good for completeness
    user_id: int
    course_id: int

class EnrollmentInDBBase(EnrollmentBase):
    class Config:
        orm_mode = True

class Enrollment(EnrollmentInDBBase): # Default schema for an enrollment
    # Potentially include nested User and Course schemas if needed for general purpose
    # user: Optional[UserSchema] = None
    # course: Optional[CourseSchema] = None
    pass

# You might also want a schema for updating an enrollment if that's allowed via API
# class EnrollmentUpdate(BaseModel):
#     progress_percentage: Optional[float] = None
#     completed_lessons: Optional[List[int]] = None
#     # etc.
