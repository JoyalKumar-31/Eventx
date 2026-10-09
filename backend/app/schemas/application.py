from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.enums import UserRole, ApplicationStatus, InvitationStatus


# --- Coordinator Application Schemas ---

class CoordinatorApplyRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: Optional[str] = Field(None, min_length=6, description="Password for account creation if not yet registered")
    phone: Optional[str] = Field(None, max_length=50)
    department: str = Field(..., min_length=2, max_length=100)
    designation: str = Field(..., min_length=2, max_length=100)
    experience: Optional[str] = Field(None, description="Relevant event management or leadership experience")
    office_location: Optional[str] = Field(None, max_length=255)


class CoordinatorApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    full_name: str
    email: str
    phone: Optional[str] = None
    department: str
    designation: str
    experience: Optional[str] = None
    office_location: Optional[str] = None
    status: ApplicationStatus
    admin_notes: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# --- Judge Application Schemas ---

class JudgeApplyRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: Optional[str] = Field(None, min_length=6, description="Password for account creation if not yet registered")
    phone: Optional[str] = Field(None, max_length=50)
    organization: str = Field(..., min_length=2, max_length=255, description="Institution, Company, or Jury Panel")
    specialization: str = Field(..., min_length=2, max_length=255, description="Domain/Expertise area (e.g. AI/ML, Web, Gaming, Arts)")
    experience: Optional[str] = Field(None, description="Judging experience, achievements, or credentials")
    bio: Optional[str] = Field(None, description="Brief biography or profile summary")


class JudgeApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    full_name: str
    email: str
    phone: Optional[str] = None
    organization: str
    specialization: str
    experience: Optional[str] = None
    bio: Optional[str] = None
    status: ApplicationStatus
    admin_notes: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# --- Sponsor Application Schemas ---

class SponsorApplyRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    industry: str = Field(..., min_length=2, max_length=100)
    contact_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    proposed_tier: Optional[str] = Field(None, max_length=50)
    proposal_message: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class SponsorApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    company_name: str
    industry: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    website: Optional[str] = None
    proposed_tier: Optional[str] = None
    proposal_message: Optional[str] = None
    status: ApplicationStatus
    admin_notes: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# --- Invitation Schemas ---

class InvitationCreateRequest(BaseModel):
    email: EmailStr
    role: UserRole = Field(..., description="Role to invite: JUDGE or SPONSOR")
    organization: Optional[str] = Field(None, max_length=255, description="Judge organization or Sponsor company name")
    specialization: Optional[str] = Field(None, max_length=255, description="Domain specialization or Industry")
    expires_in_days: int = Field(7, ge=1, le=90)


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: UserRole
    token_hash: str
    raw_token: Optional[str] = None
    invite_url: Optional[str] = None
    status: InvitationStatus
    organization: Optional[str] = None
    specialization: Optional[str] = None
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime


class InvitationVerifyResponse(BaseModel):
    valid: bool
    email: str
    role: UserRole
    organization: Optional[str] = None
    specialization: Optional[str] = None
    expires_at: datetime


class InvitationAcceptRequest(BaseModel):
    token: str = Field(..., min_length=10)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = None
    website: Optional[str] = None


class ApplicationReviewRequest(BaseModel):
    admin_notes: Optional[str] = None
