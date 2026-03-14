from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON # Ensure JSON is imported
from app.database import Base
import enum

# Define QuestionType enum here
class QuestionType(enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    # Example: TRUE_FALSE = "true_false"
    # Example: ESSAY = "essay"

class TestQuestion(Base):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("course_tests.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(SQLAlchemyEnum(QuestionType), default=QuestionType.MULTIPLE_CHOICE, nullable=False)
    options = Column(JSON, nullable=True)  # For MULTIPLE_CHOICE: [{"text": "Option A", "is_correct": True}, ...]
    correct_answer_data = Column(JSON, nullable=True) # For other types or specific storage of correct answer
    points = Column(Integer, default=1, nullable=False) # Points for this question

    test = relationship("CourseTest", back_populates="questions")

    def __repr__(self):
        return f"<TestQuestion(id={self.id}, test_id={self.test_id}, text='{self.question_text[:30]}...')>"
