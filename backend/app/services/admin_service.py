from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.user import User, RoleEnum
from app.models.event import Event, EventCategory
from app.models.registration import Registration, RegistrationStatus
from app.models.payment import Payment, PaymentStatus
from app.models.pass_attendance import Attendance
from app.schemas.admin import (
    AdminDashboardOut, AdminAnalyticsOut, MetricCardOut, CategoryDistributionOut, RecentRegistrationAdminOut
)


class AdminService:
    @staticmethod
    def get_dashboard(db: Session) -> AdminDashboardOut:
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_events = db.query(func.count(Event.id)).filter(Event.is_active == True).scalar() or 0
        total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.status == PaymentStatus.SUCCESS).scalar() or 0.0

        total_registered = db.query(func.count(Registration.id)).filter(
            Registration.status == RegistrationStatus.CONFIRMED
        ).scalar() or 0

        total_attended = db.query(func.count(Attendance.id)).scalar() or 0

        attendance_percentage = (
            round((total_attended / total_registered * 100), 1) if total_registered > 0 else 0.0
        )

        # Category distribution
        categories = db.query(
            EventCategory.name,
            func.count(Event.id).label("count")
        ).join(Event.category).group_by(EventCategory.name).all()

        category_dist = [
            CategoryDistributionOut(
                category=cat_name,
                count=cnt,
                percentage=round((cnt / total_events * 100), 1) if total_events > 0 else 0.0
            )
            for cat_name, cnt in categories
        ]

        # Recent registrations
        recent_regs = db.query(Registration).options(
            joinedload(Registration.user),
            joinedload(Registration.event)
        ).order_by(Registration.created_at.desc()).limit(10).all()

        recent_list = [
            RecentRegistrationAdminOut(
                id=r.id,
                user_name=r.user.full_name if r.user else "Anonymous",
                event_name=r.event.name if r.event else "Event",
                amount=float(r.amount),
                status=r.status.value,
                date=r.created_at.strftime("%d %b %Y, %I:%M %p")
            )
            for r in recent_regs
        ]

        metrics = [
            MetricCardOut(label="Total Users", value=f"{total_users:,}", trend="+18% this week"),
            MetricCardOut(label="Active Events", value=f"{total_events}", trend="Across 5 categories"),
            MetricCardOut(label="Total Revenue", value=f"₹{float(total_revenue):,.2f}", trend="99.4% success rate"),
            MetricCardOut(label="Live Attendance", value=f"{attendance_percentage}%", trend=f"{total_attended}/{total_registered} checked in"),
        ]

        return AdminDashboardOut(
            total_users=total_users,
            total_events=total_events,
            total_revenue=float(total_revenue),
            attendance_percentage=attendance_percentage,
            metrics=metrics,
            category_distribution=category_dist,
            recent_registrations=recent_list
        )

    @staticmethod
    def get_analytics(db: Session) -> AdminAnalyticsOut:
        # Registrations in past 7 days
        today = date.today()
        timeline = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            cnt = db.query(func.count(Registration.id)).filter(
                func.date(Registration.created_at) == day
            ).scalar() or 0
            timeline.append({"date": day.strftime("%d %b"), "count": cnt})

        # Revenue by category
        revenue_cats = db.query(
            EventCategory.name,
            func.sum(Payment.amount).label("revenue")
        ).join(Event, Event.category_id == EventCategory.id)\
         .join(Registration, Registration.event_id == Event.id)\
         .join(Payment, Payment.registration_id == Registration.id)\
         .filter(Payment.status == PaymentStatus.SUCCESS)\
         .group_by(EventCategory.name).all()

        revenue_list = [
            {"category": cat_name, "revenue": float(rev or 0.0)}
            for cat_name, rev in revenue_cats
        ]

        # Top colleges by participant count
        colleges = db.query(
            User.college,
            func.count(User.id).label("students")
        ).filter(User.college != None).group_by(User.college).order_by(func.count(User.id).desc()).limit(5).all()

        college_list = [
            {"college": col_name, "students": cnt}
            for col_name, cnt in colleges
        ]

        # Event fill rates (registered / capacity)
        events = db.query(Event).filter(Event.is_active == True).limit(8).all()
        fill_rates = [
            {
                "event": ev.name,
                "registered": ev.registered_count,
                "capacity": ev.capacity,
                "percentage": round((ev.registered_count / ev.capacity * 100), 1) if ev.capacity > 0 else 0
            }
            for ev in events
        ]

        return AdminAnalyticsOut(
            registration_timeline=timeline,
            revenue_by_category=revenue_list,
            top_colleges=college_list,
            event_fill_rates=fill_rates
        )

    @staticmethod
    def get_users_list(
        db: Session,
        search: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        query = db.query(User)
        if search:
            s = f"%{search.lower()}%"
            query = query.filter((User.full_name.ilike(s)) | (User.email.ilike(s)) | (User.college.ilike(s)))
        if role:
            query = query.filter(User.role == role.upper())
        return query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def update_user_role(db: Session, user_id: int, new_role: RoleEnum) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user
