from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, Text, Boolean, DateTime, ForeignKey, func, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class JudgeAssignment(Base):
    __tablename__ = "judge_assignments"
    __table_args__ = (UniqueConstraint("event_id", "judge_id", name="uq_event_judge"),)

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    judge_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime, server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="judges")
    judge = relationship("User", back_populates="judge_assignments")


class Evaluation(Base):
    __tablename__ = "evaluations"
    __table_args__ = (UniqueConstraint("event_id", "team_id", "judge_id", name="uq_eval_event_team_judge"),)

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    judge_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    innovation = Column(Float, default=0.0, nullable=False)
    technical_execution = Column(Float, default=0.0, nullable=False)
    presentation = Column(Float, default=0.0, nullable=False)
    total_score = Column(Float, default=0.0, nullable=False)
    remarks = Column(Text, nullable=True)

    submitted_at = Column(DateTime, server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="evaluations")
    team = relationship("Team", back_populates="evaluations")
    judge = relationship("User", back_populates="evaluations")


class EventResult(Base):
    __tablename__ = "event_results"
    __table_args__ = (UniqueConstraint("event_id", "team_id", name="uq_event_team_result"),)

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    rank = Column(Integer, nullable=False)
    average_score = Column(Float, nullable=False)
    total_evaluations = Column(Integer, default=1, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="results")
    team = relationship("Team")
