"""
tools/analytics_tools.py - Fest Analytics, Revenue, and Sponsor Management Tools
"""

from typing import Dict, Any, List




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

    # Fallback to zero-initialized statistics if database is empty or unavailable
    return {
        "overview": {
            "total_registered_students": 0,
            "total_teams": 0,
            "total_events": 0,
            "total_revenue_inr": 0.0,
            "qr_passes_scanned": 0,
            "checkin_rate_percent": 0.0,
            "sponsor_funds_inr": 0.0
        },
        "summary": "Current Fest Footfall: 0 registered students across 0 events. Total Registration Revenue: Rs. 0. QR Gate Check-in Rate: 0.0%."
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

    return {
        "total_sponsorship_amount": 0.0,
        "sponsor_count": 0,
        "sponsors": []
    }
