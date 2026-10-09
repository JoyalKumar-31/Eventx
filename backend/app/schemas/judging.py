from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.models.enums import JudgeAssignmentStatus


class JudgeAssignmentCreate(BaseModel):
    event_id: int
    judge_id: Optional[int] = None
    judge_user_id: Optional[int] = None
    round_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_judge(self):
        if not self.judge_id and not self.judge_user_id:
            raise ValueError("Either judge_id or judge_user_id must be provided")
        if not self.judge_id:
            self.judge_id = self.judge_user_id
        return self


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
    judge_user: Optional[Dict[str, Any]] = None


class ScoreCriteriaCreate(BaseModel):
    event_id: int
    round_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    max_score: Optional[float] = None
    max_points: Optional[float] = None
    weightage: float = Field(gt=0, default=1.0)

    @model_validator(mode="after")
    def resolve_max(self):
        val = self.max_score if self.max_score is not None else self.max_points
        self.max_score = float(val) if val is not None else 100.0
        return self


class ScoreCriteriaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    round_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    max_score: float
    max_points: Optional[float] = None
    weightage: float

    @model_validator(mode="after")
    def populate_alias(self):
        self.max_points = self.max_score
        return self


class ScoreEntry(BaseModel):
    criteria_id: int
    score_value: Optional[float] = None
    score: Optional[float] = None
    remarks: Optional[str] = None

    @model_validator(mode="after")
    def resolve_score_val(self):
        val = self.score_value if self.score_value is not None else self.score
        self.score_value = float(val) if val is not None else 0.0
        return self


class ScoreSubmissionRequest(BaseModel):
    registration_id: int
    scores: List[ScoreEntry]
    remarks: Optional[str] = None


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
