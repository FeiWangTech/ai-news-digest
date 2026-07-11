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
