from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.payment import PaymentStatus, PaymentMethod


class PaymentBase(BaseModel):
    course_id: int
    amount: float
    currency: str = "XOF"
    payment_method: Optional[PaymentMethod] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    status: PaymentStatus
    transaction_ref: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    course_title: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
