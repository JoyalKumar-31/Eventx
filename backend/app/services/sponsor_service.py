import json
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.sponsor import Sponsor, SponsorshipPlan, Sponsorship, SponsorPromotion
from app.schemas.sponsor import SponsorOut, SponsorshipPlanOut, SponsorPromotionOut, SponsorApplyCreate, SponsorDashboardOut


class SponsorService:
    @staticmethod
    def get_sponsors(db: Session) -> List[SponsorOut]:
        sponsors = db.query(Sponsor).filter(Sponsor.is_active == True).order_by(Sponsor.reach_count.desc()).all()
        return [SponsorOut.model_validate(s) for s in sponsors]

    @staticmethod
    def get_plans(db: Session) -> List[SponsorshipPlanOut]:
        plans = db.query(SponsorshipPlan).all()
        results = []
        for p in plans:
            perks_list = []
            if p.perks:
                try:
                    perks_list = json.loads(p.perks) if p.perks.startswith("[") else [i.strip() for i in p.perks.split(",")]
                except Exception:
                    perks_list = [p.perks]
            results.append(
                SponsorshipPlanOut(
                    id=p.id,
                    tier=p.tier,
                    price=float(p.price),
                    perks=perks_list
                )
            )
        return results

    @staticmethod
    def apply_sponsorship(db: Session, apply_in: SponsorApplyCreate) -> Sponsor:
        sponsor = Sponsor(
            name=apply_in.name,
            company_name=apply_in.company_name,
            contact_email=apply_in.contact_email,
            contact_phone=apply_in.contact_phone,
            website_url=apply_in.website_url,
            tier=apply_in.plan_tier,
            reach_count=1000,
            clicks_count=45,
            is_active=True
        )
        db.add(sponsor)
        db.commit()
        db.refresh(sponsor)
        return sponsor

    @staticmethod
    def get_sponsor_dashboard(db: Session, sponsor_id: int) -> SponsorDashboardOut:
        sponsor = db.query(Sponsor).options(
            joinedload(Sponsor.promotions)
        ).filter(Sponsor.id == sponsor_id).first()

        if not sponsor:
            raise HTTPException(status_code=404, detail="Sponsor not found")

        promos = [
            SponsorPromotionOut(
                id=p.id,
                sponsor_name=sponsor.name,
                title=p.title,
                banner_url=p.banner_url,
                target_url=p.target_url,
                impressions=p.impressions,
                clicks=p.clicks
            )
            for p in sponsor.promotions
        ]

        return SponsorDashboardOut(
            sponsor_name=sponsor.name,
            tier=sponsor.tier,
            reach_count=sponsor.reach_count,
            clicks_count=sponsor.clicks_count,
            active_promotions=promos
        )
