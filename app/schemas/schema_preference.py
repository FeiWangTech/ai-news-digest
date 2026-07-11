from datetime import datetime
from typing import Any
from pydantic import BaseModel


class PreferenceCreate(BaseModel):
    email_time: Optional[str] = None  # HH:MM
    timezone: str = "UTC"
    frequency: str = "daily"
    sources: Dict[str, Any] = {}
    topics: List[str] = []
    subscribed: bool = True


class PreferenceUpdate(BaseModel):
    email_time: Optional[str] = None
    timezone: Optional[str] = "UTC"
    frequency: Optional[str] = None
    sources: Optional[Dict[str, Any]] = None
    topics: Optional[List[str]] = None
    subscribed: Optional[bool] = None


class PreferenceResponse(BaseModel):
    id: int
    user_id: int
    email_time: Optional[str]
    timezone: str
    frequency: str
    sources: Dict[str, Any]
    topics: List[str]
    subscribed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
