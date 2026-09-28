import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Enum, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class PassStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    REVOKED = "REVOKED"


class AttendanceStatus(str, enum.Enum):
    CHECKED_IN = "CHECKED_IN"
    ABSENT = "ABSENT"


class FestPass(Base):
    __tablename__ = "passes"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, unique=True)
    qr_token = Column(String(255), unique=True, index=True, nullable=False)
    qr_image_url = Column(String(500), nullable=True)
    status = Column(Enum(PassStatus), default=PassStatus.ACTIVE, nullable=False)
    issued_at = Column(DateTime, server_default=func.now(), nullable=False)

    registration = relationship("Registration", back_populates="fest_pass")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, unique=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    scanned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.CHECKED_IN, nullable=False)
    check_in_time = Column(DateTime, server_default=func.now(), nullable=False)

    registration = relationship("Registration", back_populates="attendance")
    scanned_by = relationship("User", foreign_keys=[scanned_by_id])
