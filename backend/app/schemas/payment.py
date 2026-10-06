from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import PaymentStatus


class PaymentCreateOrderRequest(BaseModel):
    registration_id: int


class PaymentVerifyRequest(BaseModel):
    payment_id: int
    transaction_id: str
    payment_method: str = "CARD"
    simulate_status: Optional[str] = "SUCCESS"


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    payment_id: int
    registration_id: Optional[int] = None
    amount: float
    tax_amount: float
    total_amount: float
    issued_to_name: str
    issued_to_email: str
    billing_details: Optional[str] = None
    issued_at: datetime


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    registration_id: Optional[int] = None
    user_id: int
    amount: float
    currency: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_gateway: str
    gateway_order_id: Optional[str] = None
    payment_method: Optional[str] = None
    paid_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    invoice: Optional[InvoiceResponse] = None
