from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta

from app.models.user import User
from app.models.event import Event, EventCategory
from app.models.registration import Registration
from app.models.payment import Payment
from app.models.attendance import Attendance
from app.models.sponsor import Sponsorship, PromotionSlot
from app.models.enums import PaymentStatus, AttendanceStatus, EventStatus, UserRole


def get_admin_dashboard_metrics(db: Session) -> Dict[str, Any]:
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_events = db.query(func.count(Event.id)).scalar() or 0
    total_registrations = db.query(func.count(Registration.id)).scalar() or 0
    total_attendance = db.query(func.count(Attendance.id)).filter(Attendance.entry_status == AttendanceStatus.VALID).scalar() or 0
    
    total_revenue = db.query(func.coalesce(func.sum(Payment.amount), 0.0))\
                      .filter(Payment.status == PaymentStatus.SUCCESS).scalar() or 0.0
    
    total_sponsors = db.query(func.count(User.id)).filter(User.role == UserRole.SPONSOR).scalar() or 0

    # Events grouped by category
    category_counts = db.query(
        EventCategory.name,
        func.count(Event.id)
    ).join(Event, Event.category_id == EventCategory.id, isouter=True)\
     .group_by(EventCategory.name).all()
    events_by_category = {name: count for name, count in category_counts if name}

    # Registrations by status
    reg_counts = db.query(
        Registration.status,
        func.count(Registration.id)
    ).group_by(Registration.status).all()
    registrations_by_status = {status.value: count for status, count in reg_counts}

    # Recent registrations in last 24h
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_registrations = db.query(func.count(Registration.id))\
                             .filter(Registration.registered_at >= cutoff).scalar() or 0

    return {
        "total_users": total_users,
        "total_events": total_events,
        "total_registrations": total_registrations,
        "total_attendance": total_attendance,
        "total_revenue": float(total_revenue),
        "total_sponsors": total_sponsors,
        "events_by_category": events_by_category,
        "registrations_by_status": registrations_by_status,
        "recent_registrations": recent_registrations,
    }


def get_coordinator_dashboard_metrics(db: Session, coordinator_id: int) -> Dict[str, Any]:
    events_q = db.query(Event).filter(Event.coordinator_id == coordinator_id)
    total_events = events_q.count()
    active_events = events_q.filter(Event.status.in_([EventStatus.PUBLISHED, EventStatus.ONGOING])).count()

    event_ids = [e.id for e in events_q.all()]

    total_registrations = db.query(func.count(Registration.id))\
                            .filter(Registration.event_id.in_(event_ids)).scalar() if event_ids else 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_attendance = db.query(func.count(Attendance.id))\
                         .filter(Attendance.event_id.in_(event_ids),
                                 Attendance.scanned_at >= today_start,
                                 Attendance.entry_status == AttendanceStatus.VALID).scalar() if event_ids else 0

    pending_verifications = db.query(func.count(Registration.id))\
                              .filter(Registration.event_id.in_(event_ids),
                                      Registration.status == "PENDING_PAYMENT").scalar() if event_ids else 0

    upcoming_events = events_q.filter(Event.start_time >= datetime.now(timezone.utc)).count()

    return {
        "total_events": total_events,
        "active_events": active_events,
        "total_registrations": total_registrations or 0,
        "today_attendance": today_attendance or 0,
        "pending_verifications": pending_verifications or 0,
        "upcoming_events": upcoming_events,
    }


def get_sponsor_metrics(db: Session, sponsor_id: int) -> Dict[str, Any]:
    sponsorships = db.query(Sponsorship).filter(Sponsorship.sponsor_id == sponsor_id).all()
    sponsorship_ids = [s.id for s in sponsorships]

    active_sponsorships = sum(1 for s in sponsorships if s.status.value == "ACTIVE")

    total_impressions = 0
    total_clicks = 0
    active_promotions = 0

    if sponsorship_ids:
        slots = db.query(PromotionSlot).filter(PromotionSlot.sponsorship_id.in_(sponsorship_ids)).all()
        total_impressions = sum(slot.impressions_count for slot in slots)
        total_clicks = sum(slot.clicks_count for slot in slots)
        active_promotions = sum(1 for slot in slots if slot.is_active)

    return {
        "active_sponsorships": active_sponsorships,
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "active_promotions": active_promotions,
    }
