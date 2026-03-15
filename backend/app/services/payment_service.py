import uuid
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.models.payment import Payment, PaymentStatus
from app.models.course import Course
from app.models.user import User
from app.schemas.payment import PaymentCreate


def create_payment(db: Session, payment_in: PaymentCreate, user_id: int) -> Payment:
    """Create a pending payment record."""
    db_payment = Payment(
        user_id=user_id,
        course_id=payment_in.course_id,
        amount=payment_in.amount,
        currency=payment_in.currency,
        payment_method=payment_in.payment_method,
        status=PaymentStatus.pending,
        transaction_ref=f"TXN-{uuid.uuid4().hex[:12].upper()}",
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def confirm_payment(db: Session, payment_id: int, user_id: int) -> Optional[Payment]:
    """Simulate payment confirmation (in production, this would be called by a webhook)."""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == user_id,
    ).first()
    if not payment:
        return None
    if payment.status != PaymentStatus.pending:
        return payment  # Already processed
    payment.status = PaymentStatus.completed
    payment.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_user_payments(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Payment]:
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .options(joinedload(Payment.course))
        .order_by(Payment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def has_completed_payment(db: Session, user_id: int, course_id: int) -> bool:
    """Check if user has a completed payment for this course."""
    return (
        db.query(Payment)
        .filter(
            Payment.user_id == user_id,
            Payment.course_id == course_id,
            Payment.status == PaymentStatus.completed,
        )
        .first()
        is not None
    )
