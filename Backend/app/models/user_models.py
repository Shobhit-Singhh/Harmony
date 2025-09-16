import uuid
from datetime import datetime, timezone
import enum
from sqlalchemy import Integer  

from sqlalchemy import Column, String, Date, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SqlEnum
from app.core.config import Base

class UserRole(enum.Enum):
    user = "user"
    clinician = "clinician"
    admin = "admin"

class Status(enum.Enum):
    active = "active"
    banned = "banned"
    suspended = "suspended"
    deactivated = "deactivated"


class User(Base):
    __tablename__ = "users"

    # ---- Core fields ----
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    username = Column(String(50), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SqlEnum(UserRole), default=UserRole.user)
    
    # ---- Account status & verification ----
    status = Column(SqlEnum(Status), default=Status.active)
    is_verified = Column(Boolean, default=False)
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)) # note: upon refreshing the user object, updated_at will be set to current time
    
    # ---- Security & login tracking ----
    last_login_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    lockout_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    # issued_at = Column(DateTime, nullable=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),primary_key=True, default=uuid.uuid4, unique=True, index=True, nullable=False)

    # ---- Personal info ----
    full_name = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    location = Column(String(255), nullable=True)
    timezone = Column(String(50), nullable=True)

    # ---- Health & wellness ----
    primary_pillar_weights = Column(JSON, nullable=True)         # e.g., {"health": 0.4, "work": 0.3, "growth": 0.2, "relationships": 0.1}
    medications = Column(JSON, nullable=True)            
    conditions = Column(JSON, nullable=True)            
    crisis_contact = Column(String(255), nullable=True)

    # ---- Preferences & settings ----
    preferred_language = Column(String(20), nullable=True)      # e.g., "en"
    privacy_settings = Column(JSON, nullable=True)              # e.g., {"show_profile": false}

    # ---- Metadata ----
    last_updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # ---- Relationship to User ----
    user = relationship("User", back_populates="profile", uselist=False)
