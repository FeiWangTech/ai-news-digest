from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from config import settings
from jose import jwt


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PreferenceCreate(BaseModel):
    email_time: Optional[datetime] = None
    timezone: str = "UTC"
    frequency: str = "daily"
    sources: dict = {}
    topics: list[str] = []
    subscribed: bool = True


class PreferenceUpdate(BaseModel):
    email_time: Optional[datetime] = None
    timezone: Optional[str] = "UTC"
    frequency: Optional[str] = None
    sources: Optional[dict] = None
    topics: Optional[list[str]] = None
    subscribed: Optional[bool] = None


class PreferenceResponse(BaseModel):
    id: int
    user_id: int
    email_time: Optional[datetime]
    timezone: str
    frequency: str
    sources: dict
    topics: list[str]
    subscribed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DigestItemResponse(BaseModel):
    id: int
    source: str
    title: str
    url: str
    score: Optional[int]
    position: int

    model_config = {"from_attributes": True}


class DigestResponse(BaseModel):
    id: int
    user_id: int
    user_preference_id: Optional[int]
    sent_at: Optional[datetime]
    subject: str
    status: str
    created_at: datetime
    items: list[DigestItemResponse] = []

    model_config = {"from_attributes": True}


class DigestListItem(BaseModel):
    id: int
    subject: str
    status: str
    sent_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class DigestListResponse(BaseModel):
    items: list[DigestListItem]
    total: int
