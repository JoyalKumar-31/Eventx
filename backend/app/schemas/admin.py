from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import UserRole


class AdminDashboardStats(BaseModel):
    total_users: int
    total_events: int
    total_registrations: int
    total_attendance: int
    total_revenue: float
    total_sponsors: int = 0
    events_by_category: Dict[str, int] = {}
    registrations_by_status: Dict[str, int] = {}
    recent_registrations: int = 0


class CoordinatorDashboardStats(BaseModel):
    total_events: int
    active_events: int
    total_registrations: int
    today_attendance: int
    pending_verifications: int
    upcoming_events: int


class JudgeDashboardStats(BaseModel):
    assigned_events: int
    pending_evaluations: int
    completed_evaluations: int


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    is_active: bool
