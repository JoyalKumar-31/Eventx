from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db
from app.models.event import Event, EventCategory, Venue, Schedule
from app.models.registration import Registration
from app.models.enums import EventStatus
from app.schemas.event import ScheduleResponse, VenueResponse

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/stats")
def get_public_fest_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Public statistics calculated strictly from real database records.
    Never hardcoded.
    """
    events_count = db.query(func.count(Event.id)).filter(Event.status != EventStatus.DRAFT).scalar() or 0
    participants_count = db.query(func.count(Registration.id)).scalar() or 0
    categories_count = db.query(func.count(EventCategory.id)).scalar() or 0
    venues_count = db.query(func.count(Venue.id)).filter(Venue.is_active == True).scalar() or 0

    return {
        "total_events": events_count,
        "total_participants": participants_count,
        "total_categories": categories_count,
        "total_venues": venues_count
    }


@router.get("/schedules", response_model=List[ScheduleResponse])
def get_public_schedules(db: Session = Depends(get_db)):
    schedules = db.query(Schedule).order_by(Schedule.start_time.asc()).all()
    return [ScheduleResponse.model_validate(s) for s in schedules]


@router.get("/venues", response_model=List[VenueResponse])
def get_public_venues(db: Session = Depends(get_db)):
    venues = db.query(Venue).filter(Venue.is_active == True).all()
    return [VenueResponse.model_validate(v) for v in venues]
