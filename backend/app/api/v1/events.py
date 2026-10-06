import re
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.dependencies import get_db, get_current_user, get_current_user_optional, require_role
from app.models.enums import UserRole, EventStatus
from app.models.event import Event, EventCategory, Venue, EventRule, EventRound, Schedule, EventMedia
from app.models.user import User
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventListResponse,
    EventDetailResponse,
    EventCategoryCreate,
    EventCategoryResponse,
    VenueCreate,
    VenueUpdate,
    VenueResponse,
    EventMediaResponse,
    CoverImageInfo,
    EventRuleCreate,
    EventRoundCreate,
    ScheduleCreate,
    ScheduleResponse
)
from app.services.storage_service import get_storage_service, ALLOWED_MIME_TYPES, MAX_FILE_SIZE_BYTES
from app.services.audit_service import log_action

router = APIRouter(prefix="/events", tags=["Events"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def format_event_response(event: Event) -> EventListResponse:
    primary_media = next((m for m in event.media if m.is_primary), None)
    if not primary_media and event.media:
        primary_media = event.media[0]

    cover_image = CoverImageInfo(url=primary_media.public_url) if primary_media else (
        CoverImageInfo(url=event.banner_image_url) if event.banner_image_url else None
    )

    data = EventListResponse.model_validate(event)
    data.cover_image = cover_image
    return data


def format_event_detail_response(event: Event) -> EventDetailResponse:
    primary_media = next((m for m in event.media if m.is_primary), None)
    if not primary_media and event.media:
        primary_media = event.media[0]

    cover_image = CoverImageInfo(url=primary_media.public_url) if primary_media else (
        CoverImageInfo(url=event.banner_image_url) if event.banner_image_url else None
    )

    data = EventDetailResponse.model_validate(event)
    data.cover_image = cover_image
    return data


# --- Event Categories ---

@router.get("/categories", response_model=List[EventCategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(EventCategory).all()


@router.post("/categories", response_model=EventCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    req: EventCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    slug = slugify(req.name)
    existing = db.query(EventCategory).filter(or_(EventCategory.name == req.name, EventCategory.slug == slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    cat = EventCategory(
        name=req.name.strip(),
        slug=slug,
        description=req.description,
        icon=req.icon
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# --- Venues ---

@router.get("/venues", response_model=List[VenueResponse])
def list_venues(db: Session = Depends(get_db)):
    return db.query(Venue).filter(Venue.is_active == True).all()


@router.post("/venues", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(
    req: VenueCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    venue = Venue(
        name=req.name.strip(),
        building=req.building.strip(),
        floor=req.floor,
        room_number=req.room_number,
        capacity=req.capacity,
        coordinates_or_map_link=req.coordinates_or_map_link,
        is_active=req.is_active
    )
    db.add(venue)
    db.commit()
    db.refresh(venue)
    return venue


@router.put("/venues/{venue_id}", response_model=VenueResponse)
def update_venue(
    venue_id: int,
    req: VenueUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if isinstance(val, str):
            val = val.strip()
        setattr(venue, field, val)

    db.commit()
    db.refresh(venue)

    log_action(
        db,
        action="VENUE_UPDATED",
        entity_type="Venue",
        entity_id=str(venue.id),
        user_id=user.id,
        new_values=update_data
    )

    return venue


# --- Events Catalog & Discovery ---

@router.get("", response_model=List[EventListResponse])
def list_events(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    is_team: Optional[bool] = None,
    status_filter: Optional[EventStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Public and coordinator event list.
    Guests/Students see PUBLISHED, ONGOING, COMPLETED events by default.
    Coordinators and Admins can see DRAFT events.
    """
    query = db.query(Event)

    if not current_user or current_user.role not in [UserRole.ADMIN, UserRole.EVENT_COORDINATOR]:
        # Public viewer
        query = query.filter(Event.status.in_([EventStatus.PUBLISHED, EventStatus.ONGOING, EventStatus.COMPLETED, EventStatus.REGISTRATION_CLOSED]))
    elif status_filter:
        query = query.filter(Event.status == status_filter)

    if category_id:
        query = query.filter(Event.category_id == category_id)

    if is_team is not None:
        query = query.filter(Event.is_team_event == is_team)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Event.title.ilike(search_filter),
                Event.description.ilike(search_filter)
            )
        )

    events = query.order_by(Event.start_time.asc()).offset(skip).limit(limit).all()
    return [format_event_response(e) for e in events]


@router.get("/coordinator/my-events", response_model=List[EventListResponse])
def list_my_coordinated_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    query = db.query(Event)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Event.coordinator_id == current_user.id)
    events = query.order_by(Event.created_at.desc()).all()
    return [format_event_response(e) for e in events]


@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event_detail(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # If draft, only creator or admin can view
    if event.status == EventStatus.DRAFT:
        if not current_user or (current_user.role != UserRole.ADMIN and event.coordinator_id != current_user.id):
            raise HTTPException(status_code=403, detail="This event is currently in draft and not publicly accessible.")

    return format_event_detail_response(event)


# --- Event Creation & Updates ---

@router.post("", response_model=EventDetailResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    req: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    base_slug = slugify(req.title)
    slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

    # Validate category exists or fallback
    cat = db.query(EventCategory).filter(EventCategory.id == req.category_id).first()
    if not cat:
        first_cat = db.query(EventCategory).first()
        category_id = first_cat.id if first_cat else 1
    else:
        category_id = req.category_id

    # Validate venue exists if given
    venue_id = req.venue_id
    if venue_id:
        v = db.query(Venue).filter(Venue.id == venue_id).first()
        if not v:
            venue_id = None

    event = Event(
        title=req.title.strip(),
        slug=slug,
        description=req.description.strip(),
        category_id=category_id,
        coordinator_id=current_user.id,
        venue_id=venue_id,
        start_time=req.start_time,
        end_time=req.end_time,
        registration_deadline=req.registration_deadline,
        max_participants=req.max_participants,
        current_participants=0,
        is_team_event=req.is_team_event,
        min_team_size=req.min_team_size if req.is_team_event else 1,
        max_team_size=req.max_team_size if req.is_team_event else 1,
        registration_fee=req.registration_fee,
        prize_pool=req.prize_pool,
        status=req.status or EventStatus.PUBLISHED
    )
    db.add(event)
    db.flush()

    # Add rules if provided
    if req.rules:
        for idx, rule in enumerate(req.rules, start=1):
            er = EventRule(
                event_id=event.id,
                rule_order=rule.rule_order or idx,
                title=rule.title,
                description=rule.description
            )
            db.add(er)

    # Add rounds if provided
    if req.rounds:
        for idx, rnd in enumerate(req.rounds, start=1):
            ernd = EventRound(
                event_id=event.id,
                round_number=rnd.round_number or idx,
                name=rnd.name,
                description=rnd.description,
                start_time=rnd.start_time,
                end_time=rnd.end_time,
                venue_id=rnd.venue_id
            )
            db.add(ernd)

    db.commit()
    db.refresh(event)

    log_action(
        db,
        action="EVENT_CREATED",
        entity_type="Event",
        entity_id=str(event.id),
        user_id=current_user.id,
        new_values={"title": event.title, "coordinator_id": current_user.id}
    )

    return format_event_detail_response(event)


@router.put("/{event_id}", response_model=EventDetailResponse)
def update_event(
    event_id: int,
    req: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Authorize: Must be owner coordinator or admin
    if current_user.role != UserRole.ADMIN and event.coordinator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this event as you are not the assigned coordinator."
        )

    update_data = req.model_dump(exclude_unset=True)
    rules_data = update_data.pop("rules", None)
    rounds_data = update_data.pop("rounds", None)

    # Check venue_id if provided
    if "venue_id" in update_data and update_data["venue_id"]:
        v = db.query(Venue).filter(Venue.id == update_data["venue_id"]).first()
        if not v:
            update_data["venue_id"] = None

    # Check category_id if provided
    if "category_id" in update_data and update_data["category_id"]:
        cat = db.query(EventCategory).filter(EventCategory.id == update_data["category_id"]).first()
        if not cat:
            update_data.pop("category_id")

    for field, val in update_data.items():
        setattr(event, field, val)

    # Sync rules if passed
    if rules_data is not None:
        db.query(EventRule).filter(EventRule.event_id == event.id).delete()
        for idx, rule in enumerate(rules_data, start=1):
            er = EventRule(
                event_id=event.id,
                rule_order=rule.get("rule_order") or idx,
                title=rule.get("title", ""),
                description=rule.get("description", "")
            )
            db.add(er)

    # Sync rounds if passed
    if rounds_data is not None:
        db.query(EventRound).filter(EventRound.event_id == event.id).delete()
        for idx, rnd in enumerate(rounds_data, start=1):
            ernd = EventRound(
                event_id=event.id,
                round_number=rnd.get("round_number") or idx,
                name=rnd.get("name", ""),
                description=rnd.get("description"),
                start_time=rnd.get("start_time"),
                end_time=rnd.get("end_time"),
                venue_id=rnd.get("venue_id")
            )
            db.add(ernd)

    db.commit()
    db.refresh(event)

    log_action(
        db,
        action="EVENT_UPDATED",
        entity_type="Event",
        entity_id=str(event.id),
        user_id=current_user.id,
        new_values=update_data
    )

    return format_event_detail_response(event)


@router.post("/{event_id}/publish", response_model=EventDetailResponse)
def publish_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != UserRole.ADMIN and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to publish this event")

    event.status = EventStatus.PUBLISHED
    db.commit()
    db.refresh(event)

    log_action(
        db,
        action="EVENT_PUBLISHED",
        entity_type="Event",
        entity_id=str(event.id),
        user_id=current_user.id
    )

    return format_event_detail_response(event)


@router.post("/{event_id}/unpublish", response_model=EventDetailResponse)
def unpublish_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != UserRole.ADMIN and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to unpublish this event")

    event.status = EventStatus.DRAFT
    db.commit()
    db.refresh(event)

    return format_event_detail_response(event)


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != UserRole.ADMIN and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this event")

    # Prevent deleting event with active registrations
    if event.current_participants > 0:
        raise HTTPException(status_code=400, detail="Cannot delete event with existing registered participants. Change status to CANCELLED instead.")

    db.delete(event)
    db.commit()

    log_action(
        db,
        action="EVENT_DELETED",
        entity_type="Event",
        entity_id=str(event_id),
        user_id=current_user.id
    )

    return {"success": True, "message": "Event deleted successfully"}


# --- Real Event Media & Cover Image Management ---

@router.post("/{event_id}/media", response_model=EventMediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_event_media(
    event_id: int,
    file: UploadFile = File(...),
    is_primary: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    """
    Protected endpoint allowing authorized Event Coordinators and Admins to upload
    real custom cover images. Enforces strict MIME, size, dimension, and permission checks.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Strict authorization: Coordinator A cannot upload to Coordinator B's event
    if current_user.role != UserRole.ADMIN and event.coordinator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to upload images for this event."
        )

    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type '{file.content_type}'. Supported: JPG, JPEG, PNG, WEBP."
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum upload size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
        )

    storage = get_storage_service()
    storage_path, public_url, width, height = storage.save_file(
        file_bytes=contents,
        original_filename=file.filename or "event_cover.jpg",
        subfolder="events"
    )

    # If this is marked as primary, reset existing primary media for this event
    if is_primary:
        db.query(EventMedia).filter(EventMedia.event_id == event_id).update({EventMedia.is_primary: False})

    media = EventMedia(
        event_id=event.id,
        file_name=file.filename or "cover_image",
        storage_path=storage_path,
        public_url=public_url,
        mime_type=file.content_type,
        file_size=len(contents),
        width=width,
        height=height,
        is_primary=is_primary
    )
    db.add(media)

    # Also update event banner_image_url
    if is_primary:
        event.banner_image_url = public_url

    db.commit()
    db.refresh(media)

    log_action(
        db,
        action="EVENT_MEDIA_UPLOADED",
        entity_type="EventMedia",
        entity_id=str(media.id),
        user_id=current_user.id,
        new_values={"public_url": public_url, "event_id": event_id}
    )

    return media


@router.delete("/{event_id}/media/{media_id}", status_code=status.HTTP_200_OK)
def delete_event_media(
    event_id: int,
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != UserRole.ADMIN and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to remove media for this event")

    media = db.query(EventMedia).filter(EventMedia.id == media_id, EventMedia.event_id == event_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media record not found")

    storage = get_storage_service()
    storage.delete_file(media.storage_path)

    db.delete(media)
    
    # If primary deleted, reset event banner_image_url
    if media.is_primary:
        event.banner_image_url = None
        next_media = db.query(EventMedia).filter(EventMedia.event_id == event_id).first()
        if next_media:
            next_media.is_primary = True
            event.banner_image_url = next_media.public_url

    db.commit()
    return {"success": True, "message": "Media removed successfully"}


@router.put("/{event_id}/media/{media_id}/primary", response_model=EventMediaResponse)
def set_primary_media(
    event_id: int,
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.EVENT_COORDINATOR, UserRole.ADMIN))
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if current_user.role != UserRole.ADMIN and event.coordinator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to modify media for this event")

    media = db.query(EventMedia).filter(EventMedia.id == media_id, EventMedia.event_id == event_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    db.query(EventMedia).filter(EventMedia.event_id == event_id).update({EventMedia.is_primary: False})
    media.is_primary = True
    event.banner_image_url = media.public_url

    db.commit()
    db.refresh(media)
    return media
