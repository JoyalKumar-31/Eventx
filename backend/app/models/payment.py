import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    amount = Column(Numeric(10, 2), default=0.0, nullable=False)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    payment_method = Column(String(50), default="UPI", nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    paid_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    registration = relationship("Registration", back_populates="payment")
    user = relationship("User", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payment", uselist=False, cascade="all, delete-orphan")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, unique=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    invoice_url = Column(String(500), nullable=True)
    issued_at = Column(DateTime, server_default=func.now(), nullable=False)

    payment = relationship("Payment", back_populates="invoice")
