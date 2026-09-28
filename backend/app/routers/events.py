from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_role
from app.models.user import User, RoleEnum
from app.schemas.event import (
    EventOut, EventDetailOut, EventCreate, EventUpdate,
    CategoryOut, VenueOut, ScheduleItemOut, PublicStatsOut
)
from app.services.event_service import EventService

router = APIRouter(tags=["Events & Discovery"])


@router.get("/public/stats", response_model=PublicStatsOut)
def get_public_stats(db: Session = Depends(get_db)):
    """Landing page overall statistics (events, colleges, participants, prize pool)."""
    return EventService.get_public_stats(db)


@router.get("/events", response_model=List[EventOut])
def list_events(
    category: Optional[str] = Query(None, description="Filter by category name (e.g. Technical, Cultural)"),
    search: Optional[str] = Query(None, description="Search event name and description"),
    min_price: Optional[float] = Query(None, description="Minimum registration fee"),
    max_price: Optional[float] = Query(None, description="Maximum registration fee"),
    team_size: Optional[int] = Query(None, description="Filter by team size requirement"),
    event_date: Optional[date] = Query(None, description="Filter by exact event date"),
    status: Optional[str] = Query(None, description="Filter by event status (UPCOMING, ONGOING)"),
    is_featured: Optional[bool] = Query(None, description="Filter featured events"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Event discovery API supporting multiple filters: category, search query,
    price range, team size, and date.
    """
    return EventService.get_events(
        db=db,
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        team_size=team_size,
        event_date=event_date,
        status_filter=status,
        is_featured=is_featured,
        limit=limit,
        offset=offset
    )


@router.get("/events/search", response_model=List[EventOut])
def search_events(
    q: str = Query(..., min_length=1, description="Search term for events"),
    db: Session = Depends(get_db)
):
    """Convenience search endpoint for event discovery."""
    return EventService.get_events(db=db, search=q)


@router.get("/events/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """List all available event categories."""
    return EventService.get_categories(db)


@router.get("/events/venues", response_model=List[VenueOut])
def list_venues(db: Session = Depends(get_db)):
    """List all campus venues."""
    return EventService.get_venues(db)


@router.get("/events/{id}", response_model=EventDetailOut)
def get_event_detail(id: int, db: Session = Depends(get_db)):
    """
    Full event details endpoint returning About, Rules, Rounds,
    Judging Criteria, Prizes, Venue details, and FAQs.
    """
    return EventService.get_event_by_id(db, id)


@router.post("/events", response_model=EventDetailOut, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    current_user: User = Depends(require_role(RoleEnum.COORDINATOR, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new event. Restricted to Event Coordinators and Admins."""
    if not event_in.coordinator_id and current_user.role == RoleEnum.COORDINATOR:
        event_in.coordinator_id = current_user.id
    return EventService.create_event(db, event_in)


@router.put("/events/{id}", response_model=EventDetailOut)
def update_event(
    id: int,
    event_in: EventUpdate,
    current_user: User = Depends(require_role(RoleEnum.COORDINATOR, RoleEnum.ADMIN)),
    db: Session = Depends(get_db)
):
    """Update event details. Restricted to Coordinators and Admins."""
    return EventService.update_event(db, id, event_in)


@router.get("/schedule", response_model=List[ScheduleItemOut])
def get_schedule(
    day: Optional[int] = Query(None, description="Fest day number (1, 2, 3)"),
    schedule_date: Optional[date] = Query(None, description="Specific schedule date"),
    db: Session = Depends(get_db)
):
    """Fest schedule timeline and chronological events."""
    return EventService.get_schedule(db, day_number=day, schedule_date=schedule_date)
