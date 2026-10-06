from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import JudgeAssignmentStatus


class JudgeAssignmentCreate(BaseModel):
    event_id: int
    judge_id: int
    round_id: Optional[int] = None


class JudgeAssignmentResponse(BaseModel):
    id: int
    event_id: int
    event_title: str
    judge_id: int
    judge_name: str
    round_id: Optional[int] = None
    round_name: Optional[str] = None
    status: JudgeAssignmentStatus
    assigned_at: datetime


class ScoreCriteriaCreate(BaseModel):
    event_id: int
    round_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    max_score: float = Field(gt=0, default=100.0)
    weightage: float = Field(gt=0, default=1.0)


class ScoreCriteriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    round_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    max_score: float
    weightage: float


class ScoreEntry(BaseModel):
    criteria_id: int
    score_value: float
    remarks: Optional[str] = None


class ScoreSubmissionRequest(BaseModel):
    registration_id: int
    scores: List[ScoreEntry]


class ScoreResponse(BaseModel):
    id: int
    judge_assignment_id: int
    criteria_id: int
    criteria_name: str
    registration_id: int
    score_value: float
    remarks: Optional[str] = None
    submitted_at: datetime


class ResultResponse(BaseModel):
    id: int
    event_id: int
    event_title: str
    registration_id: int
    participant_name: str
    team_name: Optional[str] = None
    rank: int
    total_score: float
    award_title: Optional[str] = None
    is_published: bool
    published_at: Optional[datetime] = None


class LeaderboardEntry(BaseModel):
    registration_id: int
    participant_name: str
    team_name: Optional[str] = None
    total_score: float
    rank: int
    scores_by_criteria: dict = {}
