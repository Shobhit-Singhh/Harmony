from typing import Optional, List, Dict, Annotated
from pydantic import BaseModel, EmailStr, Field, field_validator 
from enum import Enum
from datetime import datetime, date
from uuid import UUID

#-----------------------------
# Enums
#-----------------------------


class UserRole(str, Enum):
    user = "user"
    clinician = "clinician"
    admin = "admin"


class Status(str, Enum):
    active = "active"
    banned = "banned"
    suspended = "suspended"
    deactivated = "deactivated"

#-----------------------------
# User Schemas
#-----------------------------

class UserCreate(BaseModel):
    
    # ---- Core fields ----
    username: Annotated[str, Field(min_length=3, max_length=50)]
    email: Annotated[EmailStr, Field(max_length=255)]
    phone_number: Annotated[Optional[str], Field(max_length=20, min_length=10, pattern=r'^\d+$')]
    password: Annotated[str, Field(min_length=8)]
    
    @field_validator("password")
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char in "!@#$%^&*()_-+=[]{}|;:,.<>?~" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    
    # ---- Core fields ----
    username: Annotated[Optional[str], Field(min_length=3, max_length=50)]
    email: Annotated[Optional[EmailStr], Field(max_length=255)]
    phone_number: Annotated[Optional[str], Field(max_length=20, min_length=10, pattern=r'^\d+$')]
    password: Annotated[Optional[str], Field(min_length=8)]
    role: Annotated[Optional[UserRole], Field(default=UserRole.user)]
    
    # ---- Account status & verification ----
    status: Annotated[Optional[Status], Field(default=Status.active)]
    is_verified: Annotated[Optional[bool], Field(default=False)]
    onboarding_completed: Annotated[Optional[bool], Field(default=False)]
    updated_at: Annotated[Optional[datetime], Field(default_factory=datetime.utcnow)]


class UserOut(BaseModel):
    # ---- Core fields ----
    id: Annotated[UUID, Field(description="The unique identifier for the user")]
    username: Annotated[str, Field(description="The username for the user")]
    email: Annotated[EmailStr, Field(description="The email address for the user")]
    phone_number: Annotated[Optional[str], Field(description="The phone number for the user")]
    role: Annotated[UserRole, Field(description="The role of the user")]
    
    # ---- Account status & verification ----
    status: Annotated[Optional[Status], Field(default=Status.active)]
    is_verified: Annotated[bool, Field(description="Whether the user is verified")]
    onboarding_completed: Annotated[bool, Field(description="Whether the user has completed onboarding")]
    created_at: Annotated[datetime, Field(description="The date and time the user was created")]
    updated_at: Annotated[datetime, Field(description="The date and time the user was updated")]
    
    # ---- Security & login tracking ----
    last_login_at: Annotated[Optional[datetime], Field(description="The date and time the user last logged in")]
    failed_login_attempts: Annotated[int, Field(description="Number of consecutive failed login attempts")]
    lockout_until: Annotated[Optional[datetime], Field(description="If set, the user is locked out until this time")]
    password_changed_at: Annotated[Optional[datetime], Field(description="The date and time the password was last changed")]
    
    class Config:
        from_attributes = True

class UserOutwithPassword(UserOut):
    id: Annotated[UUID, Field(description="The unique identifier for the user")]
    password_hash: Annotated[str, Field(description="The hashed password for the user")]
    
    class Config:
        from_attributes = True

#-----------------------------
# User Profile Schemas
#-----------------------------

class ProfileCreate(BaseModel):
    
    # ---- Personal info ----
    full_name: Annotated[Optional[str], Field(max_length=255)] = None
    date_of_birth: Annotated[Optional[date], Field(description="Date of birth in YYYY-MM-DD format")] = None
    gender: Annotated[Optional[str], Field(max_length=20)] = None
    location: Annotated[Optional[str], Field(max_length=255)] = None
    timezone: Annotated[Optional[str], Field(max_length=50)] = None
    
    # ---- Health & wellness ----
    primary_pillar_weights: Annotated[Optional[Dict[str, float]], Field(description="Weights for life pillars")] = None
    medications: Annotated[Optional[List[Dict[str, str]]], Field(description="List of medications")] = None
    conditions: Annotated[Optional[List[str]], Field(description="List of health conditions")] = None
    crisis_contact: Annotated[Optional[str], Field(max_length=255)] = None
    
    # ---- Preferences & settings ----
    preferred_language: Annotated[Optional[str], Field(max_length=20)] = None
    privacy_settings: Annotated[Optional[Dict[str, bool]], Field(description="Privacy settings")] = None


class ProfileUpdate(BaseModel):
    
    # ---- Personal info ----
    full_name: Annotated[Optional[str], Field(max_length=255)]
    date_of_birth: Annotated[Optional[date], Field(description="Date of birth in YYYY-MM-DD format")]
    gender: Annotated[Optional[str], Field(max_length=20)]
    location: Annotated[Optional[str], Field(max_length=255)]
    timezone: Annotated[Optional[str], Field(max_length=50)]
    
    # ---- Health & wellness ----
    primary_pillar_weights: Annotated[Optional[Dict[str, float]], Field(description="Weights for primary life pillars, e.g., {'health': 0.4, 'work': 0.3, 'growth': 0.2, 'relationships': 0.1}")]
    medications: Annotated[Optional[List[Dict[str, str]]], Field(description="List of medications with details, e.g., [{'name': 'Citalopram', 'dosage': '20mg', 'frequency': 'daily'}]")]
    conditions: Annotated[Optional[List[str]], Field(description="List of health conditions, e.g., ['depression', 'anxiety']")]
    crisis_contact: Annotated[Optional[str], Field(max_length=255)]
    
    # ---- Preferences & settings ----
    preferred_language: Annotated[Optional[str], Field(max_length=20)]
    privacy_settings: Annotated[Optional[Dict[str, bool]], Field(description="Privacy settings, e.g., {'show_profile': false}")]

    # ---- Metadata ----
    last_updated_at: Annotated[Optional[datetime], Field(default_factory=datetime.utcnow)]


class ProfileOut(BaseModel):
    
    id: Annotated[UUID, Field(description="The unique identifier for the user profile, same as user ID")]
    
    # ---- Personal info ----
    full_name: Annotated[Optional[str], Field(description="The full name of the user")]
    date_of_birth: Annotated[Optional[date], Field(description="The date of birth of the user")]    
    gender: Annotated[Optional[str], Field(max_length=20)]
    location: Annotated[Optional[str], Field(max_length=255)]
    timezone: Annotated[Optional[str], Field(max_length=50)]
    
    # ---- Health & wellness ----
    primary_pillar_weights: Annotated[Optional[Dict[str, float]], Field(description="Weights for primary life pillars, e.g., {'health': 0.4, 'work': 0.3, 'growth': 0.2, 'relationships': 0.1}")]
    medications: Annotated[Optional[List[Dict[str, str]]], Field(description="List of medications with details, e.g., [{'name': 'Citalopram', 'dosage': '20mg', 'frequency': 'daily'}]")]
    conditions: Annotated[Optional[List[str]], Field(description="List of health conditions, e.g., ['depression', 'anxiety']")]
    crisis_contact: Annotated[Optional[str], Field(description="Crisis contact information")]
    
    # ---- Preferences & settings ----
    preferred_language: Annotated[Optional[str], Field(description="Preferred language of the user")]
    privacy_settings: Annotated[Optional[Dict[str, bool]], Field(description="Privacy settings, e.g., {'show_profile': false}")]
    
    # ---- Metadata ----
    last_updated_at: Annotated[datetime, Field(description="The date and time the profile was last updated")]   
    
    class Config:
        from_attributes = True

#-----------------------------
# Combined Schemas for Responses
#-----------------------------

class UserWithProfileOut(UserOut):
    # include all fields from UserOut and an additional field 'profile' of type ProfileOut
    profile: Optional[ProfileOut] = None
    
    class Config:
        from_attributes = True