from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    registration_id: int
    payment_method: str = "UPI"


class PaymentVerify(BaseModel):
    registration_id: int
    transaction_id: str
    payment_method: str = "UPI"


class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    amount: float
    issued_at: datetime
    invoice_url: Optional[str] = None


class PaymentOut(BaseModel):
    id: int
    registration_id: int
    event_name: str
    amount: float
    transaction_id: str
    payment_method: str
    status: PaymentStatus
    paid_at: Optional[datetime] = None
    invoice: Optional[InvoiceOut] = None

    model_config = ConfigDict(from_attributes=True)
