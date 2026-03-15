from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services import payment_service, course_service
from app.dependencies import auth as auth_deps
from app.core.config import settings
from app.models.user import User as UserModel

router = APIRouter(prefix=f"{settings.API_V1_STR}/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def initiate_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user),
):
    """Initiate a payment for a course (creates a pending payment)."""
    course = course_service.get_course(db, payment_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Cours introuvable.")
    if course.is_free:
        raise HTTPException(status_code=400, detail="Ce cours est gratuit, aucun paiement nécessaire.")
    if payment_service.has_completed_payment(db, current_user.id, payment_in.course_id):
        raise HTTPException(status_code=400, detail="Vous avez déjà payé pour ce cours.")

    expected_amount = course.price or 0
    if payment_in.amount < expected_amount:
        raise HTTPException(status_code=400, detail=f"Montant insuffisant. Le prix du cours est {expected_amount} XOF.")

    payment = payment_service.create_payment(db, payment_in, current_user.id)
    return payment


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
def confirm_payment(
    payment_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user),
):
    """Confirm/simulate a payment completion. In production, this would be triggered by a payment gateway webhook."""
    payment = payment_service.confirm_payment(db, payment_id, current_user.id)
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement introuvable.")
    return payment


@router.get("/me", response_model=List[PaymentResponse])
def get_my_payments(
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user),
    skip: int = 0,
    limit: int = 50,
):
    """Get the current user's payment history."""
    return payment_service.get_user_payments(db, current_user.id, skip, limit)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_detail(
    payment_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: UserModel = Depends(auth_deps.get_current_active_user),
):
    """Get a specific payment detail (own payments only)."""
    payment = payment_service.get_payment_by_id(db, payment_id)
    if not payment or payment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Paiement introuvable.")
    return payment
