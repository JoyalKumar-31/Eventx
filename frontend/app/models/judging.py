from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.models.enums import JudgeAssignmentStatus


class JudgeAssignment(Base, TimestampMixin):
    __tablename__ = "judge_assignments"
    __table_args__ = (
        UniqueConstraint("event_id", "judge_id", "round_id", name="uq_event_judge_round"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    judge_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    round_id: Mapped[Optional[int]] = mapped_column(ForeignKey("event_rounds.id", ondelete="SET NULL"), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    status: Mapped[JudgeAssignmentStatus] = mapped_column(SQLEnum(JudgeAssignmentStatus), default=JudgeAssignmentStatus.ASSIGNED, nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="judge_assignments")
    judge: Mapped["User"] = relationship("User")
    round: Mapped[Optional["EventRound"]] = relationship("EventRound")
    scores: Mapped[List["Score"]] = relationship("Score", back_populates="judge_assignment", cascade="all, delete-orphan")


class ScoreCriteria(Base, TimestampMixin):
    __tablename__ = "score_criteria"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    round_id: Mapped[Optional[int]] = mapped_column(ForeignKey("event_rounds.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    weightage: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    event: Mapped["Event"] = relationship("Event", back_populates="score_criteria")
    scores: Mapped[List["Score"]] = relationship("Score", back_populates="criteria", cascade="all, delete-orphan")


class Score(Base, TimestampMixin):
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("judge_assignment_id", "criteria_id", "registration_id", name="uq_score_entry"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    judge_assignment_id: Mapped[int] = mapped_column(ForeignKey("judge_assignments.id", ondelete="CASCADE"), nullable=False)
    criteria_id: Mapped[int] = mapped_column(ForeignKey("score_criteria.id", ondelete="CASCADE"), nullable=False)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False)
    score_value: Mapped[float] = mapped_column(Float, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    judge_assignment: Mapped["JudgeAssignment"] = relationship("JudgeAssignment", back_populates="scores")
    criteria: Mapped["ScoreCriteria"] = relationship("ScoreCriteria", back_populates="scores")
    registration: Mapped["Registration"] = relationship("Registration", back_populates="scores")


class Result(Base, TimestampMixin):
    __tablename__ = "results"
    __table_args__ = (
        UniqueConstraint("event_id", "registration_id", "round_id", name="uq_event_reg_result"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    round_id: Mapped[Optional[int]] = mapped_column(ForeignKey("event_rounds.id", ondelete="SET NULL"), nullable=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    award_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    published_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    event: Mapped["Event"] = relationship("Event", back_populates="results")
    registration: Mapped["Registration"] = relationship("Registration", back_populates="results")
    published_by: Mapped[Optional["User"]] = relationship("User")
