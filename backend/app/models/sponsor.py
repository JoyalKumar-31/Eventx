from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.models.enums import SponsorshipTier, SponsorshipStatus, PromotionSlotType


class SponsorshipPlan(Base, TimestampMixin):
    __tablename__ = "sponsorship_plans"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tier: Mapped[SponsorshipTier] = mapped_column(SQLEnum(SponsorshipTier), unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    benefits_description: Mapped[str] = mapped_column(Text, nullable=False)
    max_slots: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    slots_booked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sponsorships: Mapped[List["Sponsorship"]] = relationship("Sponsorship", back_populates="plan")


class Sponsorship(Base, TimestampMixin):
    __tablename__ = "sponsorships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sponsor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey("sponsorship_plans.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[SponsorshipStatus] = mapped_column(SQLEnum(SponsorshipStatus), default=SponsorshipStatus.PENDING, nullable=False)
    contract_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sponsor: Mapped["User"] = relationship("User")
    plan: Mapped["SponsorshipPlan"] = relationship("SponsorshipPlan", back_populates="sponsorships")
    promotion_slots: Mapped[List["PromotionSlot"]] = relationship("PromotionSlot", back_populates="sponsorship", cascade="all, delete-orphan")


class PromotionSlot(Base, TimestampMixin):
    __tablename__ = "promotion_slots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sponsorship_id: Mapped[int] = mapped_column(ForeignKey("sponsorships.id", ondelete="CASCADE"), nullable=False)
    slot_type: Mapped[PromotionSlotType] = mapped_column(SQLEnum(PromotionSlotType), default=PromotionSlotType.BANNER, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    asset_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    target_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    impressions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sponsorship: Mapped["Sponsorship"] = relationship("Sponsorship", back_populates="promotion_slots")
