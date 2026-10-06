from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import SponsorshipTier, SponsorshipStatus, PromotionSlotType


class SponsorshipPlanCreate(BaseModel):
    name: str
    tier: SponsorshipTier
    price: float
    benefits_description: str
    max_slots: int = 5


class SponsorshipPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    tier: SponsorshipTier
    price: float
    benefits_description: str
    max_slots: int
    slots_booked: int
    is_active: bool


class PromotionSlotCreate(BaseModel):
    sponsorship_id: int
    slot_type: PromotionSlotType = PromotionSlotType.BANNER
    title: str
    asset_url: Optional[str] = None
    target_url: Optional[str] = None


class PromotionSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sponsorship_id: int
    slot_type: PromotionSlotType
    title: str
    asset_url: Optional[str] = None
    target_url: Optional[str] = None
    impressions_count: int
    clicks_count: int
    is_active: bool


class SponsorshipCreate(BaseModel):
    plan_id: int
    contract_amount: Optional[float] = None


class SponsorshipResponse(BaseModel):
    id: int
    sponsor_id: int
    sponsor_name: str
    plan_id: int
    plan_name: str
    plan_tier: SponsorshipTier
    status: SponsorshipStatus
    contract_amount: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    promotion_slots: List[PromotionSlotResponse] = []
    created_at: datetime


class SponsorStatsResponse(BaseModel):
    active_sponsorships: int
    total_impressions: int
    total_clicks: int
    active_promotions: int
