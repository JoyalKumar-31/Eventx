from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Certificate(Base, TimestampMixin):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    certificate_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False)
    award_title: Mapped[str] = mapped_column(String(150), default="Certificate of Participation", nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    verification_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    template_type: Mapped[str] = mapped_column(String(50), default="STANDARD", nullable=False)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    registration: Mapped["Registration"] = relationship("Registration", back_populates="certificate")
    user: Mapped["User"] = relationship("User", back_populates="certificates")
    event: Mapped["Event"] = relationship("Event", back_populates="certificates")
