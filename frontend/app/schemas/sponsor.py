from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import SponsorshipTier, SponsorshipStatus, PromotionSlotType


class SponsorshipPlanCreate(BaseModel):
    name: Optional[str] = None
    tier: SponsorshipTier
    price: float
    benefits_description: Optional[str] = None
    description: Optional[str] = None
    max_slots: Optional[int] = None
    max_sponsors: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.name:
            self.name = f"{self.tier.value if hasattr(self.tier, 'value') else self.tier} Tier Plan"
        if not self.benefits_description:
            self.benefits_description = self.description or "Official festival sponsorship and branding entitlements."
        if self.max_slots is None:
            self.max_slots = self.max_sponsors or 5


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
    sponsorship_id: Optional[int] = None
    slot_type: PromotionSlotType = PromotionSlotType.BANNER
    title: Optional[str] = None
    slot_name: Optional[str] = None
    asset_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    target_url: Optional[str] = None
    priority: Optional[int] = 1


class PromotionSlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sponsorship_id: int
    slot_type: PromotionSlotType
    title: str
    slot_name: Optional[str] = None
    asset_url: Optional[str] = None
    banner_image_url: Optional[str] = None
    target_url: Optional[str] = None
    impressions_count: int
    clicks_count: int
    is_active: bool

    def __init__(self, **data):
        super().__init__(**data)
        if not self.slot_name:
            self.slot_name = self.title
        if not self.banner_image_url:
            self.banner_image_url = self.asset_url


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
