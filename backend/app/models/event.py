from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.models.enums import EventStatus


class EventCategory(Base, TimestampMixin):
    __tablename__ = "event_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    events: Mapped[List["Event"]] = relationship("Event", back_populates="category")


class Venue(Base, TimestampMixin):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    building: Mapped[str] = mapped_column(String(100), nullable=False)
    floor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    room_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    coordinates_or_map_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    events: Mapped[List["Event"]] = relationship("Event", back_populates="venue")
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="venue")


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    category_id: Mapped[int] = mapped_column(ForeignKey("event_categories.id"), nullable=False)
    coordinator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    venue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("venues.id"), nullable=True)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    registration_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    max_participants: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    current_participants: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    is_team_event: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_team_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_team_size: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    registration_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    prize_pool: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[EventStatus] = mapped_column(SQLEnum(EventStatus), default=EventStatus.DRAFT, nullable=False, index=True)
    banner_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    category: Mapped["EventCategory"] = relationship("EventCategory", back_populates="events")
    coordinator: Mapped["User"] = relationship("User", back_populates="coordinated_events")
    venue: Mapped[Optional["Venue"]] = relationship("Venue", back_populates="events")
    
    rules: Mapped[List["EventRule"]] = relationship("EventRule", back_populates="event", cascade="all, delete-orphan")
    rounds: Mapped[List["EventRound"]] = relationship("EventRound", back_populates="event", cascade="all, delete-orphan")
    schedules: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="event", cascade="all, delete-orphan")
    media: Mapped[List["EventMedia"]] = relationship("EventMedia", back_populates="event", cascade="all, delete-orphan")
    registrations: Mapped[List["Registration"]] = relationship("Registration", back_populates="event")
    judge_assignments: Mapped[List["JudgeAssignment"]] = relationship("JudgeAssignment", back_populates="event")
    score_criteria: Mapped[List["ScoreCriteria"]] = relationship("ScoreCriteria", back_populates="event")
    results: Mapped[List["Result"]] = relationship("Result", back_populates="event")
    certificates: Mapped[List["Certificate"]] = relationship("Certificate", back_populates="event")


class EventRule(Base, TimestampMixin):
    __tablename__ = "event_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    rule_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="rules")


class EventRound(Base, TimestampMixin):
    __tablename__ = "event_rounds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    venue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("venues.id"), nullable=True)

    event: Mapped["Event"] = relationship("Event", back_populates="rounds")


class Schedule(Base, TimestampMixin):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    round_id: Mapped[Optional[int]] = mapped_column(ForeignKey("event_rounds.id", ondelete="SET NULL"), nullable=True)
    venue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("venues.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SCHEDULED", nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="schedules")
    venue: Mapped[Optional["Venue"]] = relationship("Venue", back_populates="schedules")


class EventMedia(Base, TimestampMixin):
    __tablename__ = "event_media"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    public_url: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="media")
