from pydantic import BaseModel
from typing import Optional, List, Any
from app.models.test_question import QuestionType

# New schema for individual question options
class QuestionOption(BaseModel):
    text: str
    is_correct: bool

class TestQuestionBase(BaseModel):
    id:Optional[int] = None
    question_text: str
    points: Optional[int] = 1
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    options: Optional[List[QuestionOption]] = None
    correct_answer_data: Optional[Any] = None # E.g. for essay, or if options don't store correctness

class TestQuestionCreate(TestQuestionBase):
    # test_id is typically a path parameter
    pass

class TestQuestionUpdate(TestQuestionBase):
    question_text: Optional[str] = None # All fields optional
    points: Optional[int] = None
    question_type: Optional[QuestionType] = None
    options: Optional[List[QuestionOption]] = None
    correct_answer_data: Optional[Any] = None


class TestQuestion(TestQuestionBase):
    id: int
    test_id: int

    class Config:
        orm_mode = True
