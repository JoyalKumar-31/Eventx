from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status

from app.models.event import (
    Event, EventCategory, Venue, EventRule, EventRound, EventPrize, EventFAQ, ScheduleItem
)
from app.models.user import User
from app.models.registration import Registration
from app.schemas.event import EventCreate, EventUpdate, PublicStatsOut


class EventService:
    @staticmethod
    def get_events(
        db: Session,
        category: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        team_size: Optional[int] = None,
        event_date: Optional[date] = None,
        status_filter: Optional[str] = None,
        is_featured: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Event]:
        query = db.query(Event).options(
            joinedload(Event.category),
            joinedload(Event.venue)
        ).filter(Event.is_active == True)

        if category:
            # Filter by category name (case-insensitive)
            query = query.join(Event.category).filter(
                func.lower(EventCategory.name) == category.lower()
            )

        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(Event.name).like(search_term),
                    func.lower(Event.description).like(search_term),
                    func.lower(Event.short_description).like(search_term)
                )
            )

        if min_price is not None:
            query = query.filter(Event.registration_fee >= min_price)

        if max_price is not None:
            query = query.filter(Event.registration_fee <= max_price)

        if team_size is not None:
            query = query.filter(
                and_(
                    Event.min_team_size <= team_size,
                    Event.max_team_size >= team_size
                )
            )

        if event_date is not None:
            query = query.filter(Event.event_date == event_date)

        if status_filter:
            query = query.filter(Event.status == status_filter.upper())

        if is_featured is not None:
            query = query.filter(Event.is_featured == is_featured)

        return query.order_by(Event.event_date.asc(), Event.start_time.asc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Event:
        event = db.query(Event).options(
            joinedload(Event.category),
            joinedload(Event.venue),
            joinedload(Event.rules),
            joinedload(Event.rounds),
            joinedload(Event.prizes),
            joinedload(Event.faqs),
            joinedload(Event.coordinator)
        ).filter(Event.id == event_id).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with id {event_id} not found"
            )
        return event

    @staticmethod
    def get_categories(db: Session) -> List[EventCategory]:
        return db.query(EventCategory).all()

    @staticmethod
    def get_venues(db: Session) -> List[Venue]:
        return db.query(Venue).all()

    @staticmethod
    def get_schedule(
        db: Session,
        day_number: Optional[int] = None,
        schedule_date: Optional[date] = None
    ) -> List[ScheduleItem]:
        query = db.query(ScheduleItem).options(
            joinedload(ScheduleItem.event),
            joinedload(ScheduleItem.venue)
        )
        if day_number:
            query = query.filter(ScheduleItem.day_number == day_number)
        if schedule_date:
            query = query.filter(ScheduleItem.date == schedule_date)

        return query.order_by(ScheduleItem.date.asc(), ScheduleItem.start_time.asc()).all()

    @staticmethod
    def get_public_stats(db: Session) -> PublicStatsOut:
        total_events = db.query(func.count(Event.id)).filter(Event.is_active == True).scalar() or 0
        total_participants = db.query(func.count(Registration.id)).scalar() or 0
        total_colleges = db.query(func.count(func.distinct(User.college))).filter(User.college != None).scalar() or 0
        total_prize_pool = db.query(func.sum(EventPrize.amount)).scalar() or 0.0
        total_categories = db.query(func.count(EventCategory.id)).scalar() or 0

        return PublicStatsOut(
            total_events=total_events,
            total_participants=total_participants,
            total_colleges=max(total_colleges, 1),
            total_prize_pool=float(total_prize_pool),
            total_categories=total_categories
        )

    @staticmethod
    def create_event(db: Session, event_in: EventCreate) -> Event:
        # Check category and venue exist
        cat = db.query(EventCategory).filter(EventCategory.id == event_in.category_id).first()
        if not cat:
            raise HTTPException(status_code=400, detail="Invalid category_id")

        venue = db.query(Venue).filter(Venue.id == event_in.venue_id).first()
        if not venue:
            raise HTTPException(status_code=400, detail="Invalid venue_id")

        event_data = event_in.model_dump(exclude={"rules", "rounds", "prizes", "faqs"})
        event = Event(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)

        if event_in.rules:
            for r in event_in.rules:
                db.add(EventRule(event_id=event.id, order=r.order, rule_text=r.rule_text))
        if event_in.rounds:
            for rd in event_in.rounds:
                db.add(EventRound(event_id=event.id, round_number=rd.round_number, title=rd.title, description=rd.description, start_time=rd.start_time))
        if event_in.prizes:
            for p in event_in.prizes:
                db.add(EventPrize(event_id=event.id, position=p.position, title=p.title, amount=p.amount, description=p.description))
        if event_in.faqs:
            for f in event_in.faqs:
                db.add(EventFAQ(event_id=event.id, question=f.question, answer=f.answer))

        # Also add a schedule item automatically
        schedule_item = ScheduleItem(
            event_id=event.id,
            venue_id=event.venue_id,
            title=event.name,
            description=event.short_description or event.description[:100],
            day_number=1,
            date=event.event_date,
            start_time=event.start_time,
            end_time=event.end_time,
            category=cat.name
        )
        db.add(schedule_item)
        db.commit()
        db.refresh(event)
        return EventService.get_event_by_id(db, event.id)

    @staticmethod
    def update_event(db: Session, event_id: int, event_in: EventUpdate) -> Event:
        event = EventService.get_event_by_id(db, event_id)
        update_data = event_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        db.commit()
        db.refresh(event)
        return event
