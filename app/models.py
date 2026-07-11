from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    preference = relationship("UserPreference", back_populates="user", uselist=False)
    digests = relationship("Digest", back_populates="user", cascade="all, delete-orphan")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    email_time = Column(Time(timezone=True), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    frequency = Column(String(20), default="daily", nullable=False)
    sources = Column(Text, default='{"hackernews": true, "techcrunch": true, "arxiv": true}', nullable=False)
    topics = Column(Text, default='[]', nullable=False)
    subscribed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="preference")
    digests = relationship("Digest", back_populates="preference", cascade="all, delete-orphan")


class Digest(Base):
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    user_preference_id = Column(Integer, ForeignKey("user_preferences.id", ondelete="CASCADE"), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    subject = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="digests")
    preference = relationship("UserPreference", back_populates="digests")
    items = relationship("DigestItem", back_populates="digest", cascade="all, delete-orphan")


class DigestItem(Base):
    __tablename__ = "digest_items"

    id = Column(Integer, primary_key=True, index=True)
    digest_id = Column(Integer, ForeignKey("digests.id", ondelete="CASCADE"), index=True, nullable=False)
    source = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    score = Column(Integer, nullable=True)
    position = Column(Integer, nullable=False)

    digest = relationship("Digest", back_populates="items")
