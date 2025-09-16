import uuid
from datetime import datetime, timezone
import enum

from sqlalchemy import Column, String, Date, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SqlEnum
from app.core.config import Base

class UserRole(enum.Enum):
    user = "user"
    clinician = "clinician"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    username = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.user)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),primary_key=True, default=uuid.uuid4, unique=True, index=True, nullable=False)

    # Core demographic & personal info
    full_name = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    location = Column(String(255), nullable=True)
    timezone = Column(String(50), nullable=True)

    # Health & mental wellness info
    primary_pillar_weights = Column(JSON, nullable=True)         # e.g., {"health": 0.4, "work": 0.3, "growth": 0.2, "relationships": 0.1}
    medications = Column(JSON, nullable=True)            
    conditions = Column(JSON, nullable=True)            
    crisis_contact = Column(String(255), nullable=True)

    # personalization
    preferred_language = Column(String(20), nullable=True)      # e.g., "en"
    privacy_settings = Column(JSON, nullable=True)              # e.g., {"show_profile": false}


    # Tracking info
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    onboarding_completed = Column(Boolean, default=False)

    # Relationship to User
    user = relationship("User", back_populates="profile", uselist=False)