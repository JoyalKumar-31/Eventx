from typing import List, Optional
from pydantic import BaseModel


class UserBasicOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    college: Optional[str] = None


class StudentStatisticsOut(BaseModel):
    registered: int
    upcoming: int
    certificates: int


class NextEventOut(BaseModel):
    id: int
    name: str
    date: str
    time: str
    venue: str
    category: Optional[str] = None


class RecommendationOut(BaseModel):
    id: int
    name: str
    category: str
    match: int  # percentage, e.g. 94
    registration_fee: float
    venue: str


class StudentDashboardOut(BaseModel):
    user: UserBasicOut
    statistics: StudentStatisticsOut
    next_event: Optional[NextEventOut] = None
    recommendations: List[RecommendationOut] = []
