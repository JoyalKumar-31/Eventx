from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole
from app.models.payment import Payment, Invoice
from app.models.user import User
from app.schemas.payment import (
    PaymentCreateOrderRequest,
    PaymentVerifyRequest,
    PaymentResponse,
    InvoiceResponse
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


def format_payment_response(p: Payment) -> PaymentResponse:
    inv = None
    if p.invoice:
        inv = InvoiceResponse.model_validate(p.invoice)
    res = PaymentResponse.model_validate(p)
    res.invoice = inv
    return res


@router.post("/create-order", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment_order(
    req: PaymentCreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.ADMIN))
):
    payment = PaymentService.create_payment_order(
        db=db,
        registration_id=req.registration_id,
        user_id=current_user.id
    )
    return format_payment_response(payment)


@router.post("/verify", response_model=PaymentResponse)
def verify_payment(
    req: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.ADMIN))
):
    payment = PaymentService.verify_and_complete_payment(
        db=db,
        payment_id=req.payment_id,
        transaction_id=req.transaction_id,
        payment_method=req.payment_method,
        simulate_status=req.simulate_status or "SUCCESS",
        user_id=current_user.id if current_user.role != UserRole.ADMIN else None
    )
    return format_payment_response(payment)


@router.get("/my", response_model=List[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).order_by(Payment.created_at.desc()).all()
    return [format_payment_response(p) for p in payments]


@router.get("/invoices/{invoice_number}", response_model=InvoiceResponse)
def get_invoice(
    invoice_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Authorize: user must own payment or be admin
    payment = inv.payment
    if current_user.role != UserRole.ADMIN and payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to view this invoice")

    return InvoiceResponse.model_validate(inv)


@router.get("/all", response_model=List[PaymentResponse])
def list_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    payments = db.query(Payment).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    return [format_payment_response(p) for p in payments]
