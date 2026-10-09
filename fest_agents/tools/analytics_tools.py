"""
tools/analytics_tools.py - Fest Analytics, Revenue, and Sponsor Management Tools
"""

from typing import Dict, Any, List

# Sample fest analytics data
FEST_ANALYTICS_DATA = {
    "total_registered_students": 1420,
    "total_teams": 310,
    "total_events": 18,
    "total_revenue_inr": 285000,
    "qr_passes_scanned": 1180,
    "checkin_rate_percent": 83.1,
    "sponsor_funds_inr": 450000
}

SPONSORSHIPS_DB = [
    {
        "tier": "Title Sponsor",
        "company": "TechNova Innovations",
        "contribution_inr": 250000,
        "deliverables": "Main Stage Naming, VIP Lounge, App Splash Screen",
        "status": "Confirmed"
    },
    {
        "tier": "Associate Sponsor",
        "company": "CloudSprint Labs",
        "contribution_inr": 120000,
        "deliverables": "Hackathon Title Partner, Booth in Quadrangle",
        "status": "Confirmed"
    },
    {
        "tier": "Beverage Partner",
        "company": "HydraCola Energy",
        "contribution_inr": 80000,
        "deliverables": "Beverage stalls at all food courts & arenas",
        "status": "Confirmed"
    }
]


def get_fest_analytics() -> Dict[str, Any]:
    """
    Returns high-level statistics for Admin & Coordinators dashboard from MySQL or fallback data.
    """
    try:
        from sqlalchemy import func
        from app.db.session import SessionLocal
        from app.models.user import User
        from app.models.enums import UserRole, EventStatus, PaymentStatus
        from app.models.event import Event
        from app.models.registration import Registration, Team
        from app.models.payment import Payment
        from app.models.attendance import Attendance
        from app.models.sponsor import SponsorPackage

        db = SessionLocal()
        try:
            total_students = db.query(User).filter(User.role == UserRole.STUDENT).count()
            total_teams = db.query(Team).count()
            total_events = db.query(Event).filter(Event.status != EventStatus.DRAFT).count()
            
            revenue_sum = db.query(func.sum(Payment.amount)).filter(Payment.status == PaymentStatus.COMPLETED).scalar() or 0.0
            scanned_count = db.query(Attendance).count()
            total_regs = db.query(Registration).count()
            
            checkin_rate = round((scanned_count / total_regs * 100), 1) if total_regs > 0 else 0.0
            sponsor_funds = db.query(func.sum(SponsorPackage.price)).scalar() or 0.0

            analytics_data = {
                "total_registered_students": total_students,
                "total_teams": total_teams,
                "total_events": total_events,
                "total_revenue_inr": float(revenue_sum),
                "qr_passes_scanned": scanned_count,
                "checkin_rate_percent": checkin_rate,
                "sponsor_funds_inr": float(sponsor_funds)
            }
            return {
                "overview": analytics_data,
                "summary": (
                    f"Current Fest Footfall: {total_students} registered students across {total_events} events. "
                    f"Total Registration Revenue: Rs. {float(revenue_sum):,.0f}. "
                    f"Sponsor Contributions: Rs. {float(sponsor_funds):,.0f}. "
                    f"QR Gate Check-in Rate: {checkin_rate}% ({scanned_count}/{total_regs})."
                )
            }
        finally:
            db.close()
    except Exception:
        pass

    # Fallback to sample data
    return {
        "overview": FEST_ANALYTICS_DATA,
        "summary": (
            f"Current Fest Footfall: {FEST_ANALYTICS_DATA['total_registered_students']} participants "
            f"across {FEST_ANALYTICS_DATA['total_events']} events. "
            f"Total Registration Revenue: Rs. {FEST_ANALYTICS_DATA['total_revenue_inr']:,}. "
            f"QR Gate Check-in Rate: {FEST_ANALYTICS_DATA['checkin_rate_percent']}%."
        )
    }


def get_sponsor_reports() -> Dict[str, Any]:
    """
    Returns active sponsorship tiers, companies, contributions, and deliverables from MySQL or fallback DB.
    """
    try:
        from app.db.session import SessionLocal
        from app.models.sponsor import SponsorPackage, SponsorInquiry

        db = SessionLocal()
        try:
            packages = db.query(SponsorPackage).filter(SponsorPackage.is_active == True).all()
            inquiries = db.query(SponsorInquiry).all()
            if packages:
                sponsors_list = []
                total_rev = 0.0
                for pkg in packages:
                    pkg_price = float(pkg.price) if pkg.price else 0.0
                    total_rev += pkg_price
                    sponsors_list.append({
                        "tier": pkg.tier_name,
                        "company": pkg.name,
                        "contribution_inr": pkg_price,
                        "deliverables": pkg.description or "Main Stage Branding & VIP passes",
                        "status": "Available" if pkg.slots_available > 0 else "Sold Out"
                    })
                return {
                    "total_sponsorship_amount": total_rev,
                    "sponsor_count": len(packages),
                    "sponsors": sponsors_list
                }
        finally:
            db.close()
    except Exception:
        pass

    total_sponsor_revenue = sum(s["contribution_inr"] for s in SPONSORSHIPS_DB)
    return {
        "total_sponsorship_amount": total_sponsor_revenue,
        "sponsor_count": len(SPONSORSHIPS_DB),
        "sponsors": SPONSORSHIPS_DB
    }
