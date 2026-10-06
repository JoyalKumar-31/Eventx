from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.models.enums import AttendanceStatus


class Attendance(Base, TimestampMixin):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id", ondelete="CASCADE"), index=True, nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False)
    round_id: Mapped[Optional[int]] = mapped_column(ForeignKey("event_rounds.id", ondelete="SET NULL"), nullable=True)
    scanned_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    entry_status: Mapped[AttendanceStatus] = mapped_column(SQLEnum(AttendanceStatus), default=AttendanceStatus.VALID, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    registration: Mapped["Registration"] = relationship("Registration", back_populates="attendance_records")
    event: Mapped["Event"] = relationship("Event")
    scanned_by: Mapped["User"] = relationship("User")
