from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sponsor import (
    SponsorOut, SponsorshipPlanOut, SponsorApplyCreate, SponsorDashboardOut
)
from app.services.sponsor_service import SponsorService

router = APIRouter(prefix="/sponsors", tags=["Sponsors & Partnerships"])


@router.get("", response_model=List[SponsorOut])
def get_sponsors(db: Session = Depends(get_db)):
    """Public showcase of official FESTORA partners and sponsors."""
    return SponsorService.get_sponsors(db)


@router.get("/plans", response_model=List[SponsorshipPlanOut])
def get_sponsorship_plans(db: Session = Depends(get_db)):
    """Available corporate sponsorship packages and promotional perks."""
    return SponsorService.get_plans(db)


@router.post("/apply", response_model=SponsorOut, status_code=status.HTTP_201_CREATED)
def apply_for_sponsorship(apply_in: SponsorApplyCreate, db: Session = Depends(get_db)):
    """Submit a corporate sponsorship partnership application."""
    sponsor = SponsorService.apply_sponsorship(db, apply_in)
    return SponsorOut.model_validate(sponsor)


@router.get("/dashboard/{id}", response_model=SponsorDashboardOut)
def get_sponsor_dashboard(id: int, db: Session = Depends(get_db)):
    """Sponsor analytics dashboard showing brand reach, impressions, and click-throughs."""
    return SponsorService.get_sponsor_dashboard(db, id)
