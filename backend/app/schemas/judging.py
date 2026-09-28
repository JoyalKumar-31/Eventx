from typing import List, Optional
from pydantic import BaseModel, Field


class EvaluationCreate(BaseModel):
    team_id: int
    innovation: float = Field(..., ge=0, le=100, description="Innovation score (0-100)")
    technical_execution: float = Field(..., ge=0, le=100, description="Technical execution score (0-100)")
    presentation: float = Field(..., ge=0, le=100, description="Presentation score (0-100)")
    remarks: Optional[str] = None


class EvaluationOut(BaseModel):
    id: int
    team_id: int
    team_name: str
    judge_name: str
    innovation: float
    technical_execution: float
    presentation: float
    total_score: float
    remarks: Optional[str] = None


class LeaderboardEntryOut(BaseModel):
    rank: int
    team_id: int
    team_name: str
    score: float
    evaluations_count: int


class EventLeaderboardOut(BaseModel):
    event_id: int
    event_name: str
    is_published: bool
    leaderboard: List[LeaderboardEntryOut]


class JudgeEventTeamOut(BaseModel):
    id: int
    name: str
    members_count: int
    is_evaluated: bool
    evaluation: Optional[EvaluationOut] = None


class JudgeDashboardOut(BaseModel):
    judge_name: str
    assigned_events: List[dict]
