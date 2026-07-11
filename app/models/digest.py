from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from enum import Enum


class DigestStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class Digest(Base):
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    user_preference_id = Column(Integer, ForeignKey("user_preferences.id", ondelete="CASCADE"), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    status = Column(SQLEnum(DigestStatus, native_enum=False), default=DigestStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="digests")
    preference = relationship("UserPreference", back_populates="digests")
    items = relationship("DigestItem", back_populates="digest", cascade="all, delete-orphan")
