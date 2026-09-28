from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class SponsorshipPlan(Base):
    __tablename__ = "sponsorship_plans"

    id = Column(Integer, primary_key=True, index=True)
    tier = Column(String(50), unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    perks = Column(Text, nullable=False)  # JSON string or description of perks

    sponsorships = relationship("Sponsorship", back_populates="plan")


class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    company_name = Column(String(150), nullable=True)
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    tier = Column(String(50), default="Gold", nullable=False)
    reach_count = Column(Integer, default=0, nullable=False)
    clicks_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    sponsorships = relationship("Sponsorship", back_populates="sponsor", cascade="all, delete-orphan")
    promotions = relationship("SponsorPromotion", back_populates="sponsor", cascade="all, delete-orphan")


class Sponsorship(Base):
    __tablename__ = "sponsorships"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("sponsorship_plans.id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="APPROVED", nullable=False)
    contract_date = Column(DateTime, server_default=func.now(), nullable=False)

    sponsor = relationship("Sponsor", back_populates="sponsorships")
    plan = relationship("SponsorshipPlan", back_populates="sponsorships")


class SponsorPromotion(Base):
    __tablename__ = "sponsor_promotions"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    banner_url = Column(String(500), nullable=True)
    target_url = Column(String(500), nullable=True)
    impressions = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    sponsor = relationship("Sponsor", back_populates="promotions")
