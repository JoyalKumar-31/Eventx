import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text, func
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class RoleEnum(str, enum.Enum):
    STUDENT = "STUDENT"
    COORDINATOR = "COORDINATOR"
    JUDGE = "JUDGE"
    ADMIN = "ADMIN"
    SPONSOR = "SPONSOR"
    GUEST = "GUEST"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=True)
    college = Column(String(200), nullable=True)
    department = Column(String(100), nullable=True)
    year_of_study = Column(Integer, nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.STUDENT, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")
    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")
    created_teams = relationship("Team", back_populates="leader", foreign_keys="Team.leader_id")
    team_memberships = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    invitations = relationship("TeamInvitation", back_populates="invitee", foreign_keys="TeamInvitation.invitee_id")
    payments = relationship("Payment", back_populates="user")
    certificates = relationship("Certificate", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    judge_assignments = relationship("JudgeAssignment", back_populates="judge")
    evaluations = relationship("Evaluation", back_populates="judge")


class UserInterest(Base):
    __tablename__ = "user_interests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="interests")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
