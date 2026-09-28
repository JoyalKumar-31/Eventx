from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.user import User, UserInterest
from app.models.event import Event, EventCategory
from app.models.registration import Registration, RegistrationStatus
from app.models.certificate import Certificate
from app.schemas.student import (
    StudentDashboardOut, UserBasicOut, StudentStatisticsOut, NextEventOut, RecommendationOut
)


class StudentService:
    @staticmethod
    def get_dashboard(db: Session, user: User) -> StudentDashboardOut:
        # Count registrations
        total_registered = db.query(func.count(Registration.id)).filter(
            Registration.user_id == user.id,
            Registration.status.in_([RegistrationStatus.CONFIRMED, RegistrationStatus.PENDING_PAYMENT])
        ).scalar() or 0

        # Count upcoming registered events
        today = date.today()
        upcoming_count = db.query(func.count(Registration.id)).join(Registration.event).filter(
            Registration.user_id == user.id,
            Registration.status == RegistrationStatus.CONFIRMED,
            Event.event_date >= today
        ).scalar() or 0

        # Count certificates
        certificates_count = db.query(func.count(Certificate.id)).filter(
            Certificate.user_id == user.id
        ).scalar() or 0

        # Find the next event
        next_reg = db.query(Registration).join(Registration.event).options(
            joinedload(Registration.event).joinedload(Event.venue),
            joinedload(Registration.event).joinedload(Event.category)
        ).filter(
            Registration.user_id == user.id,
            Registration.status == RegistrationStatus.CONFIRMED,
            Event.event_date >= today
        ).order_by(Event.event_date.asc(), Event.start_time.asc()).first()

        next_event_data = None
        if next_reg and next_reg.event:
            ev = next_reg.event
            next_event_data = NextEventOut(
                id=ev.id,
                name=ev.name,
                date=ev.event_date.strftime("%d %b").upper() if hasattr(ev.event_date, "strftime") else str(ev.event_date),
                time=ev.start_time.strftime("%I:%M %p") if hasattr(ev.start_time, "strftime") else str(ev.start_time),
                venue=ev.venue.name if ev.venue else "Campus",
                category=ev.category.name if ev.category else None
            )

        # Recommendations based on user interests
        user_interests = [i.category.lower() for i in db.query(UserInterest).filter(UserInterest.user_id == user.id).all()]
        registered_event_ids = [
            r.event_id for r in db.query(Registration.event_id).filter(Registration.user_id == user.id).all()
        ]

        # Find events matching interests not already registered
        query = db.query(Event).join(Event.category).options(
            joinedload(Event.venue),
            joinedload(Event.category)
        ).filter(
            Event.is_active == True,
            ~Event.id.in_(registered_event_ids) if registered_event_ids else True
        )

        all_candidate_events = query.limit(10).all()
        recommendations: List[RecommendationOut] = []

        for ev in all_candidate_events:
            match_score = 75
            if user_interests and ev.category and ev.category.name.lower() in user_interests:
                match_score = 94
            elif ev.is_featured:
                match_score = 88

            recommendations.append(
                RecommendationOut(
                    id=ev.id,
                    name=ev.name,
                    category=ev.category.name if ev.category else "General",
                    match=match_score,
                    registration_fee=float(ev.registration_fee),
                    venue=ev.venue.name if ev.venue else "Main Ground"
                )
            )

        # Sort recommendations by highest match score
        recommendations.sort(key=lambda x: x.match, reverse=True)

        return StudentDashboardOut(
            user=UserBasicOut(
                id=user.id,
                name=user.full_name,
                email=user.email,
                college=user.college
            ),
            statistics=StudentStatisticsOut(
                registered=total_registered,
                upcoming=upcoming_count,
                certificates=certificates_count
            ),
            next_event=next_event_data,
            recommendations=recommendations[:5]
        )

    @staticmethod
    def get_my_events(db: Session, user: User) -> List[Registration]:
        return db.query(Registration).options(
            joinedload(Registration.event).joinedload(Event.category),
            joinedload(Registration.event).joinedload(Event.venue),
            joinedload(Registration.team),
            joinedload(Registration.fest_pass)
        ).filter(Registration.user_id == user.id).order_by(Registration.created_at.desc()).all()
