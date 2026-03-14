from pydantic import BaseModel
from typing import Optional, List, Any
from app.schemas.test_question import TestQuestionCreate, TestQuestionBase

class CourseTestBase(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None # In minutes
    passing_score: Optional[float] = None # Percentage e.g. 70.0 for 70%
    max_attempts: Optional[int] = None

class CourseTestCreate(CourseTestBase):
    # section_id is usually a path parameter or handled by service linking it to a section
    questions: Optional[List[TestQuestionCreate]] = []

class CourseTestUpdate(CourseTestBase):
    title: Optional[str] = None # All fields optional
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    passing_score: Optional[float] = None
    max_attempts: Optional[int] = None
    questions: Optional[List[TestQuestionCreate]] = None # Or List[TestQuestionUpdate] if IDs are known

class CourseTest(CourseTestBase):
    id: int
    section_id: Optional[int] = None # Can be null if test is independent
    questions: List[TestQuestionBase] = []

    class Config:
        orm_mode = True

# --- Schemas for Test Submissions/Attempts by Students ---

class StudentAnswerSchema(BaseModel):
    question_id: int
    # The actual answer format will depend on question_type
    # For MCQ, it could be a list of selected option IDs or the option ID itself
    # For text answers, it could be a string
    answer_data: Optional[Any] = None # Flexible field for various answer types

class TestSubmissionPayloadSchema(BaseModel):
    answers: List[StudentAnswerSchema]
    # Optional: client could report time taken, etc.
    # time_taken_seconds: Optional[int] = None

# Schema for the data that record_test_attempt in service layer expects for questions_summary
# This mirrors TestAttemptQuestionSummary from enrollment.py but is for input to service
class TestQuestionAttemptSummaryInputSchema(BaseModel):
    question_id: int
    is_correct: Optional[bool] = None # Client might not know this; service should determine
    points_earned: Optional[float] = None # Client might not know this; service should determine
    # any other data that needs to be recorded per question in the attempt

# This schema is what the router endpoint for submitting a test might accept
# if the client is expected to provide score and passed status (as current service signature suggests)
class TestSubmissionWithScoreSchema(BaseModel):
    score: float
    passed: bool
    questions_summary: Optional[List[TestQuestionAttemptSummaryInputSchema]] = None
    # Optionally, include raw answers if service needs them too
    # answers: Optional[List[StudentAnswerSchema]] = None
