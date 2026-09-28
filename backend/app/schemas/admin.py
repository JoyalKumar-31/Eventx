from typing import List, Optional
from pydantic import BaseModel


class MetricCardOut(BaseModel):
    label: str
    value: str
    trend: Optional[str] = None


class CategoryDistributionOut(BaseModel):
    category: str
    count: int
    percentage: float


class RecentRegistrationAdminOut(BaseModel):
    id: int
    user_name: str
    event_name: str
    amount: float
    status: str
    date: str


class AdminDashboardOut(BaseModel):
    total_users: int
    total_events: int
    total_revenue: float
    attendance_percentage: float
    metrics: List[MetricCardOut] = []
    category_distribution: List[CategoryDistributionOut] = []
    recent_registrations: List[RecentRegistrationAdminOut] = []


class AdminAnalyticsOut(BaseModel):
    registration_timeline: List[dict] = []
    revenue_by_category: List[dict] = []
    top_colleges: List[dict] = []
    event_fill_rates: List[dict] = []
