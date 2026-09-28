from datetime import datetime, date, time
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Date, Time, DateTime,
    Boolean, ForeignKey, Float, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    building = Column(String(150), nullable=True)
    room_number = Column(String(50), nullable=True)
    capacity = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    map_url = Column(String(500), nullable=True)

    events = relationship("Event", back_populates="venue")
    schedules = relationship("ScheduleItem", back_populates="venue")


class EventCategory(Base):
    __tablename__ = "event_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)

    events = relationship("Event", back_populates="category")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("event_categories.id"), nullable=False, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=False, index=True)
    coordinator_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    description = Column(Text, nullable=False)
    short_description = Column(String(300), nullable=True)
    banner_url = Column(String(500), nullable=True)

    registration_fee = Column(Numeric(10, 2), default=0.0, nullable=False)
    capacity = Column(Integer, default=100, nullable=False)
    registered_count = Column(Integer, default=0, nullable=False)

    min_team_size = Column(Integer, default=1, nullable=False)
    max_team_size = Column(Integer, default=1, nullable=False)

    event_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    registration_deadline = Column(DateTime, nullable=False)

    status = Column(String(50), default="UPCOMING", nullable=False)  # UPCOMING, ONGOING, COMPLETED, CANCELLED
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    category = relationship("EventCategory", back_populates="events")
    venue = relationship("Venue", back_populates="events")
    coordinator = relationship("User", foreign_keys=[coordinator_id])
    rules = relationship("EventRule", back_populates="event", cascade="all, delete-orphan", order_by="EventRule.order")
    rounds = relationship("EventRound", back_populates="event", cascade="all, delete-orphan", order_by="EventRound.round_number")
    prizes = relationship("EventPrize", back_populates="event", cascade="all, delete-orphan", order_by="EventPrize.position")
    faqs = relationship("EventFAQ", back_populates="event", cascade="all, delete-orphan")
    schedules = relationship("ScheduleItem", back_populates="event")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
    judges = relationship("JudgeAssignment", back_populates="event", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="event", cascade="all, delete-orphan")
    results = relationship("EventResult", back_populates="event", cascade="all, delete-orphan")


class EventRule(Base):
    __tablename__ = "event_rules"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    order = Column(Integer, default=1, nullable=False)
    rule_text = Column(Text, nullable=False)

    event = relationship("Event", back_populates="rules")


class EventRound(Base):
    __tablename__ = "event_rounds"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    round_number = Column(Integer, default=1, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="rounds")


class EventPrize(Base):
    __tablename__ = "event_prizes"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False)
    title = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), default=0.0, nullable=False)
    description = Column(Text, nullable=True)

    event = relationship("Event", back_populates="prizes")


class EventFAQ(Base):
    __tablename__ = "event_faqs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    event = relationship("Event", back_populates="faqs")


class ScheduleItem(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    day_number = Column(Integer, default=1, nullable=False)
    date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    category = Column(String(100), nullable=True)

    event = relationship("Event", back_populates="schedules")
    venue = relationship("Venue", back_populates="schedules")
