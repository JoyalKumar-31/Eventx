from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.models.enums import TeamStatus, TeamMemberRole, RegistrationStatus


class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    leader_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invite_code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    status: Mapped[TeamStatus] = mapped_column(SQLEnum(TeamStatus), default=TeamStatus.FORMING, nullable=False)

    event: Mapped["Event"] = relationship("Event")
    leader: Mapped["User"] = relationship("User")
    members: Mapped[List["TeamMember"]] = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    registrations: Mapped[List["Registration"]] = relationship("Registration", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[TeamMemberRole] = mapped_column(SQLEnum(TeamMemberRole), default=TeamMemberRole.MEMBER, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    team: Mapped["Team"] = relationship("Team", back_populates="members")
    user: Mapped["User"] = relationship("User")


class Registration(Base, TimestampMixin):
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_event_user_reg"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    registration_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[RegistrationStatus] = mapped_column(
        SQLEnum(RegistrationStatus),
        default=RegistrationStatus.PENDING_PAYMENT,
        nullable=False,
        index=True
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    qr_code_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="registrations")
    user: Mapped["User"] = relationship("User", back_populates="registrations")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="registrations")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="registration")
    attendance_records: Mapped[List["Attendance"]] = relationship("Attendance", back_populates="registration")
    scores: Mapped[List["Score"]] = relationship("Score", back_populates="registration")
    results: Mapped[List["Result"]] = relationship("Result", back_populates="registration")
    certificate: Mapped[Optional["Certificate"]] = relationship("Certificate", back_populates="registration", uselist=False)
