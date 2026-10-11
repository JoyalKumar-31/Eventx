from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.enums import UserRole


class StudentProfileCreate(BaseModel):
    college_name: str
    student_id_number: str
    department: str
    year_of_study: str


class CoordinatorProfileCreate(BaseModel):
    department: str
    designation: str
    office_location: Optional[str] = None


class JudgeProfileCreate(BaseModel):
    organization: str
    specialization: str
    bio: Optional[str] = None


class SponsorProfileCreate(BaseModel):
    company_name: str
    industry: str
    website: Optional[str] = None
    contact_phone: Optional[str] = None


class StudentRegisterRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None
    college_name: Optional[str] = None
    student_id_number: Optional[str] = None
    department: Optional[str] = None
    year_of_study: Optional[str] = "1st Year"
    student_profile: Optional[StudentProfileCreate] = None


class UserRegisterRequest(BaseModel):
    """
    Standard registration schema. Role is strictly assigned as STUDENT on the server.
    Any client-supplied role or profile fields are ignored to prevent privilege escalation.
    """
    model_config = ConfigDict(extra="ignore")

    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = None
    college_name: Optional[str] = None
    student_id_number: Optional[str] = None
    department: Optional[str] = None
    year_of_study: Optional[str] = "1st Year"
    student_profile: Optional[StudentProfileCreate] = None
    role: Optional[str] = None  # Ignored by server; role is always STUDENT



class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    college_name: str
    student_id_number: str
    department: str
    year_of_study: str


class CoordinatorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department: str
    designation: str
    office_location: Optional[str] = None


class JudgeProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization: str
    specialization: str
    bio: Optional[str] = None


class SponsorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company_name: str
    industry: str
    website: Optional[str] = None
    contact_phone: Optional[str] = None
    logo_url: Optional[str] = None


class UserDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    student_profile: Optional[StudentProfileResponse] = None
    coordinator_profile: Optional[CoordinatorProfileResponse] = None
    judge_profile: Optional[JudgeProfileResponse] = None
    sponsor_profile: Optional[SponsorProfileResponse] = None


class UserProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    full_name: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None  # Alias for frontend tolerance
    college_name: Optional[str] = None
    student_id_number: Optional[str] = None
    roll_number: Optional[str] = None  # Alias for frontend tolerance
    department: Optional[str] = None
    year_of_study: Optional[Any] = None  # Can accept string or int from frontend form

