from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    email_time = Column(String(5), nullable=True)  # HH:MM string for simplicity
    timezone = Column(String(50), default="UTC", nullable=False)
    frequency = Column(String(20), default="daily", nullable=False)
    sources = Column(Text, default='{"hackernews": true, "techcrunch": true, "arxiv": true}', nullable=False)
    topics = Column(Text, default='[]', nullable=False)
    subscribed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="preference")
    digests = relationship("Digest", back_populates="preference", cascade="all, delete-orphan")
