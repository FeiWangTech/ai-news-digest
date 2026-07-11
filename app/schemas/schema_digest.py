from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


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
    items: List["DigestItemResponse"] = []

    model_config = {"from_attributes": True}


class DigestListItem(BaseModel):
    id: int
    subject: str
    status: str
    sent_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class DigestListResponse(BaseModel):
    items: List[DigestListItem]
    total: int
