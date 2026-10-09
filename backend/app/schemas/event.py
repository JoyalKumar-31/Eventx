from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import EventStatus


class EventCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class EventCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None


class VenueCreate(BaseModel):
    name: str
    building: str
    floor: Optional[str] = None
    room_number: Optional[str] = None
    capacity: int = 100
    coordinates_or_map_link: Optional[str] = None
    is_active: bool = True


class VenueUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    room_number: Optional[str] = None
    capacity: Optional[int] = None
    coordinates_or_map_link: Optional[str] = None
    is_active: Optional[bool] = None


class VenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: str
    floor: Optional[str] = None
    room_number: Optional[str] = None
    capacity: int
    coordinates_or_map_link: Optional[str] = None
    is_active: bool


class EventRuleCreate(BaseModel):
    rule_order: int = 1
    title: str
    description: str


class EventRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_order: int
    title: str
    description: str


class EventRoundCreate(BaseModel):
    round_number: int = 1
    name: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    venue_id: Optional[int] = None


class EventRoundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    round_number: int
    name: str
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    venue_id: Optional[int] = None


class ScheduleCreate(BaseModel):
    event_id: int
    round_id: Optional[int] = None
    venue_id: Optional[int] = None
    title: str
    start_time: datetime
    end_time: datetime
    status: str = "SCHEDULED"


class ScheduleEventBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    category: Optional[EventCategoryResponse] = None
    status: Optional[str] = None
    is_team_event: Optional[bool] = False


class ScheduleRoundBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    round_number: Optional[int] = 1


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    round_id: Optional[int] = None
    venue_id: Optional[int] = None
    title: str
    start_time: datetime
    end_time: datetime
    status: str
    venue: Optional[VenueResponse] = None
    event: Optional[ScheduleEventBrief] = None
    round: Optional[ScheduleRoundBrief] = None


class EventMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    file_name: str
    storage_path: str
    public_url: str
    mime_type: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    is_primary: bool


class CoverImageInfo(BaseModel):
    url: str


class EventCreate(BaseModel):
    title: str
    description: str
    category_id: int
    venue_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    registration_deadline: datetime
    max_participants: int = 50
    is_team_event: bool = False
    min_team_size: int = 1
    max_team_size: int = 1
    registration_fee: float = 0.0
    prize_pool: Optional[str] = None
    status: Optional[EventStatus] = EventStatus.PUBLISHED
    rules: Optional[List[EventRuleCreate]] = None
    rounds: Optional[List[EventRoundCreate]] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    venue_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    max_participants: Optional[int] = None
    is_team_event: Optional[bool] = None
    min_team_size: Optional[int] = None
    max_team_size: Optional[int] = None
    registration_fee: Optional[float] = None
    prize_pool: Optional[str] = None
    status: Optional[EventStatus] = None
    rules: Optional[List[EventRuleCreate]] = None
    rounds: Optional[List[EventRoundCreate]] = None


class CoordinatorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class EventListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: str
    category_id: int
    category: Optional[EventCategoryResponse] = None
    venue_id: Optional[int] = None
    venue: Optional[VenueResponse] = None
    start_time: datetime
    end_time: datetime
    registration_deadline: datetime
    max_participants: int
    current_participants: int
    is_team_event: bool
    min_team_size: int
    max_team_size: int
    registration_fee: float
    prize_pool: Optional[str] = None
    status: EventStatus
    banner_image_url: Optional[str] = None
    cover_image: Optional[CoverImageInfo] = None
    created_at: datetime


class EventDetailResponse(EventListResponse):
    model_config = ConfigDict(from_attributes=True)

    coordinator: Optional[CoordinatorBrief] = None
    rules: List[EventRuleResponse] = []
    rounds: List[EventRoundResponse] = []
    schedules: List[ScheduleResponse] = []
    media: List[EventMediaResponse] = []
