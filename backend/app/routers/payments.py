from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.payment import PaymentVerify, PaymentOut, InvoiceOut
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments & Invoices"])


@router.post("", response_model=PaymentOut)
def process_payment(
    payment_in: PaymentVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process payment for a registration, mark registration confirmed,
    issue an official invoice and generate the QR Fest Pass.
    """
    return PaymentService.process_payment(
        db=db,
        user=current_user,
        registration_id=payment_in.registration_id,
        transaction_id=payment_in.transaction_id,
        payment_method=payment_in.payment_method
    )


@router.get("/my", response_model=List[PaymentOut])
def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List of all payments and invoices made by user."""
    return PaymentService.get_my_payments(db, current_user)
