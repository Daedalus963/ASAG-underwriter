import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field

from app.models import Role


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, description="Minimum 10 characters.")
    role: Role = Role.AGENT


class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: Role
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Applicants ----------
class ApplicantCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    latitude: float = Field(ge=6.0, le=38.0, description="Must fall within India's approximate bounding box.")
    longitude: float = Field(ge=67.0, le=98.0, description="Must fall within India's approximate bounding box.")
    crop_type: Optional[str] = None
    farm_size_acres: Optional[float] = Field(default=None, ge=0, le=10000)
    loan_amount_inr: Optional[float] = Field(default=None, ge=0, le=100_000_000)


class ApplicantOut(ApplicantCreate):
    id: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# ---------- Assessment ----------
class AssessmentOut(BaseModel):
    id: str
    applicant_id: str
    agri_data: Optional[dict[str, Any]]
    emotion_data: Optional[dict[str, Any]]
    combined_score: Optional[dict[str, Any]]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
