from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.enums import UserRole, SponsorshipStatus, SponsorshipTier
from app.models.sponsor import SponsorshipPlan, Sponsorship, PromotionSlot
from app.models.user import User
from app.schemas.sponsor import (
    SponsorshipPlanCreate,
    SponsorshipPlanResponse,
    SponsorshipCreate,
    SponsorshipResponse,
    PromotionSlotCreate,
    PromotionSlotResponse,
    SponsorStatsResponse
)
from app.services.analytics_service import get_sponsor_metrics
from app.services.audit_service import log_action

router = APIRouter(prefix="/sponsors", tags=["Sponsors"])


def format_sponsorship(s: Sponsorship) -> SponsorshipResponse:
    return SponsorshipResponse(
        id=s.id,
        sponsor_id=s.sponsor_id,
        sponsor_name=s.sponsor.full_name,
        plan_id=s.plan_id,
        plan_name=s.plan.name,
        plan_tier=s.plan.tier,
        status=s.status,
        contract_amount=s.contract_amount,
        start_date=s.start_date,
        end_date=s.end_date,
        promotion_slots=[PromotionSlotResponse.model_validate(slot) for slot in s.promotion_slots],
        created_at=s.created_at
    )


@router.get("/plans", response_model=List[SponsorshipPlanResponse])
def list_sponsorship_plans(db: Session = Depends(get_db)):
    return db.query(SponsorshipPlan).filter(SponsorshipPlan.is_active == True).all()


@router.post("/plans", response_model=SponsorshipPlanResponse, status_code=status.HTTP_201_CREATED)
def create_sponsorship_plan(
    req: SponsorshipPlanCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(UserRole.ADMIN))
):
    plan = SponsorshipPlan(
        name=req.name.strip(),
        tier=req.tier,
        price=req.price,
        benefits_description=req.benefits_description,
        max_slots=req.max_slots,
        slots_booked=0,
        is_active=True
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/select-plan", response_model=SponsorshipResponse, status_code=status.HTTP_201_CREATED)
def select_sponsorship_plan(
    req: SponsorshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SPONSOR, UserRole.ADMIN))
):
    plan = db.query(SponsorshipPlan).filter(SponsorshipPlan.id == req.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Sponsorship plan not found")

    if plan.slots_booked >= plan.max_slots:
        raise HTTPException(status_code=400, detail="All slots for this sponsorship tier have been filled.")

    amount = req.contract_amount or plan.price

    sponsorship = Sponsorship(
        sponsor_id=current_user.id,
        plan_id=plan.id,
        status=SponsorshipStatus.ACTIVE,
        contract_amount=amount,
        start_date=datetime.now(timezone.utc)
    )
    db.add(sponsorship)
    plan.slots_booked += 1
    db.commit()
    db.refresh(sponsorship)

    log_action(
        db,
        action="SPONSORSHIP_SUBSCRIBED",
        entity_type="Sponsorship",
        entity_id=str(sponsorship.id),
        user_id=current_user.id,
        new_values={"plan_tier": plan.tier.value, "amount": amount}
    )

    return format_sponsorship(sponsorship)


@router.get("/my-sponsorships", response_model=List[SponsorshipResponse])
def get_my_sponsorships(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SPONSOR, UserRole.ADMIN))
):
    sponsorships = db.query(Sponsorship).filter(Sponsorship.sponsor_id == current_user.id).all()
    return [format_sponsorship(s) for s in sponsorships]


@router.post("/promotions", response_model=PromotionSlotResponse, status_code=status.HTTP_201_CREATED)
def create_promotion_slot(
    req: PromotionSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SPONSOR, UserRole.ADMIN))
):
    sponsorship = None
    if req.sponsorship_id:
        sponsorship = db.query(Sponsorship).filter(Sponsorship.id == req.sponsorship_id).first()
        if not sponsorship:
            raise HTTPException(status_code=404, detail="Sponsorship record not found")
        if current_user.role != UserRole.ADMIN and sponsorship.sponsor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized to add promotions to this sponsorship")
    else:
        sponsorship = db.query(Sponsorship).filter(Sponsorship.sponsor_id == current_user.id).order_by(Sponsorship.id.desc()).first()
        if not sponsorship:
            first_plan = db.query(SponsorshipPlan).filter(SponsorshipPlan.is_active == True).first()
            if first_plan:
                sponsorship = Sponsorship(
                    sponsor_id=current_user.id,
                    plan_id=first_plan.id,
                    status=SponsorshipStatus.ACTIVE,
                    contract_amount=first_plan.price,
                    start_date=datetime.now(timezone.utc)
                )
                db.add(sponsorship)
                first_plan.slots_booked += 1
                db.commit()
                db.refresh(sponsorship)
            else:
                raise HTTPException(status_code=400, detail="Please select a sponsorship plan first.")

    title_val = req.title or req.slot_name or "Promotional Banner"
    asset_val = req.asset_url or req.banner_image_url

    slot = PromotionSlot(
        sponsorship_id=sponsorship.id,
        slot_type=req.slot_type,
        title=title_val.strip(),
        asset_url=asset_val.strip() if asset_val else None,
        target_url=req.target_url.strip() if req.target_url else None,
        impressions_count=0,
        clicks_count=0,
        is_active=True
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.get("/promotions/active", response_model=List[PromotionSlotResponse])
def list_active_promotions(db: Session = Depends(get_db)):
    """Public promotional slots for event cards and sponsors section."""
    slots = db.query(PromotionSlot).filter(PromotionSlot.is_active == True).all()
    # Increment impression counts in batch
    for s in slots:
        s.impressions_count += 1
    db.commit()
    return slots


@router.post("/promotions/{slot_id}/track-click")
def track_promotion_click(
    slot_id: int,
    db: Session = Depends(get_db)
):
    slot = db.query(PromotionSlot).filter(PromotionSlot.id == slot_id).first()
    if slot:
        slot.clicks_count += 1
        db.commit()
    return {"success": True}


@router.get("/metrics", response_model=SponsorStatsResponse)
def get_my_sponsor_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SPONSOR, UserRole.ADMIN))
):
    metrics = get_sponsor_metrics(db, current_user.id)
    return SponsorStatsResponse(**metrics)
