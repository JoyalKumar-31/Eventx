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
    Returns high-level statistics for Admin & Coordinators dashboard.
    """
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
    Returns active sponsorship tiers, companies, contributions, and deliverables.
    """
    total_sponsor_revenue = sum(s["contribution_inr"] for s in SPONSORSHIPS_DB)
    return {
        "total_sponsorship_amount": total_sponsor_revenue,
        "sponsor_count": len(SPONSORSHIPS_DB),
        "sponsors": SPONSORSHIPS_DB
    }
