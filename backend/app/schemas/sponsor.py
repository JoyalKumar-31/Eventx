from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class SponsorshipPlanOut(BaseModel):
    id: int
    tier: str
    price: float
    perks: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class SponsorPromotionOut(BaseModel):
    id: int
    sponsor_name: str
    title: str
    banner_url: Optional[str] = None
    target_url: Optional[str] = None
    impressions: int
    clicks: int


class SponsorOut(BaseModel):
    id: int
    name: str
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    tier: str
    reach_count: int
    clicks_count: int

    model_config = ConfigDict(from_attributes=True)


class SponsorApplyCreate(BaseModel):
    name: str
    company_name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    website_url: Optional[str] = None
    plan_tier: str = "Gold"


class SponsorDashboardOut(BaseModel):
    sponsor_name: str
    tier: str
    reach_count: int
    clicks_count: int
    active_promotions: List[SponsorPromotionOut] = []
