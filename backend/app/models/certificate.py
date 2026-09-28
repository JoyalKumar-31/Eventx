from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String(100), unique=True, index=True, nullable=False)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(150), default="Certificate of Participation", nullable=False)
    pdf_url = Column(String(500), nullable=True)
    issue_date = Column(DateTime, server_default=func.now(), nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)

    registration = relationship("Registration", back_populates="certificate")
    user = relationship("User", back_populates="certificates")
    event = relationship("Event")
