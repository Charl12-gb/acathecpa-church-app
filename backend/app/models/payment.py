from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentMethod(enum.Enum):
    mobile_money = "mobile_money"
    card = "card"
    bank_transfer = "bank_transfer"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="XOF", nullable=False)
    status = Column(SQLAlchemyEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    payment_method = Column(SQLAlchemyEnum(PaymentMethod), nullable=True)
    transaction_ref = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="payments")
    course = relationship("Course", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, user={self.user_id}, course={self.course_id}, status={self.status.value})>"
