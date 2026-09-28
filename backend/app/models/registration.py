import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, Numeric, DateTime, Enum, ForeignKey, func, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class RegistrationStatus(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True, index=True)

    status = Column(
        Enum(RegistrationStatus),
        default=RegistrationStatus.PENDING_PAYMENT,
        nullable=False,
        index=True
    )
    amount = Column(Numeric(10, 2), default=0.0, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
    team = relationship("Team", back_populates="registrations")
    payment = relationship("Payment", back_populates="registration", uselist=False)
    fest_pass = relationship("FestPass", back_populates="registration", uselist=False)
    attendance = relationship("Attendance", back_populates="registration", uselist=False)
    certificate = relationship("Certificate", back_populates="registration", uselist=False)
