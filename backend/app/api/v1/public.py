from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db
from app.models.event import Event, EventCategory, Venue, Schedule, EventRound
from app.models.registration import Registration
from app.models.enums import EventStatus
from app.schemas.event import ScheduleResponse, VenueResponse, ScheduleEventBrief, ScheduleRoundBrief, EventCategoryResponse

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
    """
    Returns complete festival schedule timetable synthesized from
    explicit schedule entries and all active events with rounds.
    """
    schedules = db.query(Schedule).order_by(Schedule.start_time.asc()).all()
    schedule_event_ids = {s.event_id for s in schedules}
    results = []

    for s in schedules:
        evt_brief = None
        if s.event:
            cat_resp = EventCategoryResponse.model_validate(s.event.category) if s.event.category else None
            evt_brief = ScheduleEventBrief(
                id=s.event.id,
                title=s.event.title,
                category=cat_resp,
                status=s.event.status.value if hasattr(s.event.status, "value") else str(s.event.status),
                is_team_event=s.event.is_team_event
            )
        round_brief = None
        if s.round_id:
            rnd = db.query(EventRound).filter(EventRound.id == s.round_id).first()
            if rnd:
                round_brief = ScheduleRoundBrief(id=rnd.id, name=rnd.name, round_number=rnd.round_number)
        venue_resp = VenueResponse.model_validate(s.venue) if s.venue else None

        results.append(ScheduleResponse(
            id=s.id,
            event_id=s.event_id,
            round_id=s.round_id,
            venue_id=s.venue_id,
            title=s.title,
            start_time=s.start_time,
            end_time=s.end_time,
            status=s.status,
            venue=venue_resp,
            event=evt_brief,
            round=round_brief
        ))

    # For events without explicit schedule rows, include them so timetable is always populated
    events = db.query(Event).filter(Event.status != EventStatus.DRAFT).order_by(Event.start_time.asc()).all()
    virtual_id = 100000
    for evt in events:
        if evt.id not in schedule_event_ids:
            cat_resp = EventCategoryResponse.model_validate(evt.category) if evt.category else None
            evt_brief = ScheduleEventBrief(
                id=evt.id,
                title=evt.title,
                category=cat_resp,
                status=evt.status.value if hasattr(evt.status, "value") else str(evt.status),
                is_team_event=evt.is_team_event
            )
            venue_resp = VenueResponse.model_validate(evt.venue) if evt.venue else None

            if evt.rounds and len(evt.rounds) > 0:
                for rnd in evt.rounds:
                    virtual_id += 1
                    r_venue = db.query(Venue).filter(Venue.id == rnd.venue_id).first() if rnd.venue_id else evt.venue
                    r_venue_resp = VenueResponse.model_validate(r_venue) if r_venue else venue_resp
                    results.append(ScheduleResponse(
                        id=virtual_id,
                        event_id=evt.id,
                        round_id=rnd.id,
                        venue_id=rnd.venue_id or evt.venue_id,
                        title=f"{evt.title} - {rnd.name}",
                        start_time=rnd.start_time or evt.start_time,
                        end_time=rnd.end_time or evt.end_time,
                        status=evt.status.value if hasattr(evt.status, "value") else str(evt.status),
                        venue=r_venue_resp,
                        event=evt_brief,
                        round=ScheduleRoundBrief(id=rnd.id, name=rnd.name, round_number=rnd.round_number)
                    ))
            else:
                virtual_id += 1
                results.append(ScheduleResponse(
                    id=virtual_id,
                    event_id=evt.id,
                    round_id=None,
                    venue_id=evt.venue_id,
                    title=evt.title,
                    start_time=evt.start_time,
                    end_time=evt.end_time,
                    status=evt.status.value if hasattr(evt.status, "value") else str(evt.status),
                    venue=venue_resp,
                    event=evt_brief,
                    round=None
                ))

    results.sort(key=lambda x: x.start_time)
    return results


@router.get("/venues", response_model=List[VenueResponse])
def get_public_venues(db: Session = Depends(get_db)):
    venues = db.query(Venue).filter(Venue.is_active == True).all()
    return [VenueResponse.model_validate(v) for v in venues]
