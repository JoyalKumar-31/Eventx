from datetime import date, time, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class VenueOut(BaseModel):
    id: int
    name: str
    building: Optional[str] = None
    room_number: Optional[str] = None
    capacity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    map_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VenueCreate(BaseModel):
    name: str
    building: Optional[str] = None
    room_number: Optional[str] = None
    capacity: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    map_url: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class EventRuleOut(BaseModel):
    id: int
    order: int
    rule_text: str

    model_config = ConfigDict(from_attributes=True)


class EventRuleCreate(BaseModel):
    order: int = 1
    rule_text: str


class EventRoundOut(BaseModel):
    id: int
    round_number: int
    title: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EventRoundCreate(BaseModel):
    round_number: int
    title: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None


class EventPrizeOut(BaseModel):
    id: int
    position: int
    title: str
    amount: float
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EventPrizeCreate(BaseModel):
    position: int
    title: str
    amount: float
    description: Optional[str] = None


class EventFAQOut(BaseModel):
    id: int
    question: str
    answer: str

    model_config = ConfigDict(from_attributes=True)


class EventFAQCreate(BaseModel):
    question: str
    answer: str


class EventOut(BaseModel):
    id: int
    name: str
    category: CategoryOut
    venue: VenueOut
    short_description: Optional[str] = None
    description: str
    banner_url: Optional[str] = None
    registration_fee: float
    capacity: int
    registered_count: int
    min_team_size: int
    max_team_size: int
    event_date: date
    start_time: time
    end_time: time
    registration_deadline: datetime
    status: str
    is_active: bool
    is_featured: bool

    model_config = ConfigDict(from_attributes=True)


class EventDetailOut(EventOut):
    rules: List[EventRuleOut] = []
    rounds: List[EventRoundOut] = []
    prizes: List[EventPrizeOut] = []
    faqs: List[EventFAQOut] = []

    model_config = ConfigDict(from_attributes=True)


class EventCreate(BaseModel):
    name: str
    category_id: int
    venue_id: int
    coordinator_id: Optional[int] = None
    description: str
    short_description: Optional[str] = None
    banner_url: Optional[str] = None
    registration_fee: float = 0.0
    capacity: int = 100
    min_team_size: int = 1
    max_team_size: int = 1
    event_date: date
    start_time: time
    end_time: time
    registration_deadline: datetime
    is_featured: bool = False
    rules: Optional[List[EventRuleCreate]] = None
    rounds: Optional[List[EventRoundCreate]] = None
    prizes: Optional[List[EventPrizeCreate]] = None
    faqs: Optional[List[EventFAQCreate]] = None


class EventUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    venue_id: Optional[int] = None
    coordinator_id: Optional[int] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    banner_url: Optional[str] = None
    registration_fee: Optional[float] = None
    capacity: Optional[int] = None
    min_team_size: Optional[int] = None
    max_team_size: Optional[int] = None
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    registration_deadline: Optional[datetime] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class ScheduleItemOut(BaseModel):
    id: int
    event_id: Optional[int] = None
    event_name: Optional[str] = None
    venue: Optional[VenueOut] = None
    title: str
    description: Optional[str] = None
    day_number: int
    date: date
    start_time: time
    end_time: time
    category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PublicStatsOut(BaseModel):
    total_events: int
    total_participants: int
    total_colleges: int
    total_prize_pool: float
    total_categories: int
