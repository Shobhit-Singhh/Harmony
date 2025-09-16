from __future__ import annotations

from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user_models import User, UserProfile, UserRole  
from v1.user_schema import (
    UserCreate,
    UserUpdate, 
    UserOut,
    ProfileCreate,
    ProfileUpdate,
    ProfileOut,
    UserWithProfileOut,
)

from app.core import security
from app.crud import user_crud
import logging


logger = logging.getLogger(__name__)

# Domain-specific exceptions
class ServiceError(Exception):
    """Generic service error (bad input, conflict, etc.)."""


class NotFoundError(ServiceError):
    """Raised when an entity is not found."""


class ConflictError(ServiceError):
    """Raised on conflict such as duplicate email."""


class PermissionError(ServiceError):
    """Raised when user doesn't have permission for the operation."""


class ValidationError(ServiceError):
    """Raised when input validation fails."""


# User State Management Service
class UserState(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"


# -----------------------------
# User Service
# -----------------------------


class UserService:
    """
    Complete service layer orchestrating CRUD + business rules.
    Handles user lifecycle, profile management, and state transitions.
    """

    def __init__(self,db: Session):
        self.db = db

    # ---------- Generic user operations ----------

    def create_user(self, user_in: UserCreate) -> UserOut:
        
        # Check for duplicates
        if user_crud.get_user_by_email(self.db, email=user_in.email):
            raise ConflictError("Email already registered")
        
        if user_crud.get_user_by_phone(self.db, phone_number=user_in.phone_number):
            raise ConflictError("Phone number already registered")
        
        # Hash password
        hashed_pw = security.get_password_hash(user_in.password)
        
        try:
            # Create user
            db_user = user_crud.create_user(self.db, user_in=user_in, password_hash=hashed_pw)
            
            # Auto-create empty profile
            profile_data = ProfileCreate() # Empty Dummy profile
            profile = user_crud.create_profile(self.db, user_id=db_user.id, profile_create=profile_data)
            
            # Return combined user + profile 
            user_dict = db_user.dict()
            user_dict['profile'] = profile.dict()
            
            return UserWithProfileOut(**user_dict)
        except IntegrityError as e:
            self.db.rollback()
            logger.exception(f"Integrity error during user creation: {e}")
            raise ConflictError("User creation failed due to integrity error") from e # e.g., unique constraint
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Unexpected error during user creation: {e}")
            raise ServiceError("User creation failed due to unexpected error") from e # catch-all for other DB errors

    def authenticate_user(self, email: str, password: str) -> UserOut:
        # Get DB model (not schema) from CRUD
        user: User = user_crud.get_user_by_email(self.db, email=email)
        if not user:
            raise NotFoundError("User not found")
        
        if not user.is_active:
            raise PermissionError("User account is inactive")
        
        if not security.verify_password(password, user.password_hash):
            raise ValidationError("Incorrect password")
        
        try:
            # Update last login timestamp
            user_crud.update_last_login(self.db, user.id)
            updated_user: User = user_crud.get_user_by_id(self.db, user.id)

            # Convert SQLAlchemy model → Pydantic schema for safe output
            return UserOut.model_validate(updated_user)

        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error updating last login: {e}")
            raise ServiceError("Failed to update last login") from e

    def get_user(self, user_id: UUID, requesting_user: Optional[User] = None, 
                 include_sensitive: bool = False) -> UserOut:
        """
        Read user by ID with role-based access control.
        
        Args:
            user_id: Target user ID
            requesting_user: User making the request (for permission checks)
            include_sensitive: Whether to include sensitive fields (admin only)
        """
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")

        # Permission check: users can view their own data, admins can view all
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to view this user")

        return user

    def get_user_with_profile(self, user_id: UUID, requesting_user: Optional[User] = None) -> UserWithProfileOut:
        """
        Get user with their profile data.
        """
        user = self.get_user(user_id, requesting_user)
        profile = user_crud.get_profile_by_user_id(self.db, user_id)
        
        user_dict = user.dict()
        user_dict['profile'] = profile.dict() if profile else None
        return UserWithProfileOut(**user_dict)

    def list_users(self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None,
                    requesting_user: Optional[User] = None) -> List[UserOut]:
            """
            List users with pagination and filtering (admin only).
            
            Args:
                skip: Offset for pagination
                limit: Limit for pagination
                filters: Optional filters (role, is_active, etc.)
                requesting_user: User making the request
            """
            # Permission check: only admins can list users
            if requesting_user and requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to list users")

            return user_crud.list_users(self.db, skip=skip, limit=limit, filters=filters)

    def update_user(self, user_id: UUID, user_in: UserUpdate, requesting_user: Optional[User] = None) -> UserOut:
        user = user_crud.get_user_by_id(self.db, user_id)
        
        if not user:
            raise NotFoundError("User not found")
        
        # Permission check: users can update their own data, admins can update all
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to update this user") 
        
        # Additional validation for role changes (admin only)
        if user_in.role and requesting_user.role != UserRole.admin:
            raise PermissionError("Only admins can change user roles")
        
        try: 
            updated_user = user_crud.update_user(self.db, db_user=user, user_update=user_in)
            return updated_user

        except Exception as e:
            self.db.rollback()
            logger.exception(f"Unexpected error during user update: {e}")
            raise ServiceError("User update failed due to unexpected error") from e

    def change_password(self, user_id: UUID, old_password: str, new_password: str, requesting_user: Optional[User] = None) -> None:
        user = user_crud.get_user_by_id(self.db, user_id)
        
        if not user:
            raise NotFoundError("User not found")
        
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to change this user's password")
            
        if requesting_user and requesting_user.role != UserRole.admin:
            if not security.verify_password(old_password, user.password_hash):
                raise ValidationError("Old password is incorrect")
            
        # Hash new password
        new_hashed_pw = security.hash_password(new_password)
        
        try:
            user_crud.update_user_password(self.db, user_id=user_id, new_password_hash=new_hashed_pw)
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Unexpected error during password change: {e}")
            raise ServiceError("Password change failed due to unexpected error") from e

    def change_user_state(self, user_id: UUID, target_state: UserState, requesting_user: Optional[User]) -> UserOut:
        """
        User can transition through states: Active ↔ Deactivated.
        Admins can transition through all states.
        """
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")

        # Self-user rule (non-admins)
        if requesting_user and requesting_user.id == user_id and requesting_user.role != UserRole.admin:
            if target_state not in {UserState.ACTIVE, UserState.DEACTIVATED}:
                raise PermissionError("Users can only activate/deactivate their own account")

        # Other-user rule
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to manage other users")

        try:
            updated_user = user_crud.update_user_state(self.db, user_id=user_id, target_state=target_state)
            return updated_user
        except Exception as e:
            self.db.rollback()
            logger.exception("Unexpected error during user state change for %s: %s", user_id, e)
            raise ServiceError("User state change failed due to unexpected error") from e

    # ---------- Profile operations ----------

    def create_profile(self, user_id: UUID, profile_in: ProfileCreate, requesting_user: Optional[User] = None) -> ProfileOut:
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to create profile for this user")
            
        existing_profile = user_crud.get_profile_by_user_id(self.db, user_id)
        # cheack if its only contains id and nothing else (dummy profile)
        if existing_profile and existing_profile.full_name is not None:
            raise ConflictError("Profile already exists")
        
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")
        
        try:
            profile = user_crud.create_profile(self.db, user_id=user_id, profile_create=profile_in)
            return profile
        except IntegrityError as e:
            self.db.rollback()
            logger.exception(f"Integrity error during profile creation: {e}")
            raise ConflictError("Profile creation failed due to integrity error") from e
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Unexpected error during profile creation: {e}")
            raise ServiceError("Profile creation failed due to unexpected error") from e

    def get_profile(self, user_id: UUID, requesting_user: Optional[User] = None) -> Optional[ProfileOut]:
        profile = user_crud.get_profile_by_user_id(self.db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")
            return None
        
        if requesting_user and requesting_user.id != user_id:
            profile = self._apply_privacy_filter(profile, requesting_user)
        
        return profile

    def update_profile(self, user_id: UUID, profile_in: ProfileUpdate, requesting_user: Optional[User] = None) -> ProfileOut:
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to update this profile")

        profile = user_crud.get_profile_by_user_id(self.db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")

        self._validate_profile_data(profile_in)

        try:
            updated_profile = user_crud.update_profile(self.db, db_profile=profile, profile_update=profile_in)
            return updated_profile
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Unexpected error during profile update: {e}")
            raise ServiceError("Profile update failed due to unexpected error") from e

    def delete_profile(self, user_id: UUID, requesting_user: Optional[User] = None) -> None:
        """
        Delete profile (admin only or self).
        """
        # Permission check
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to delete this profile")

        profile = user_crud.get_profile_by_user_id(self.db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")

        try:
            user_crud.delete_profile(self.db, profile)
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed deleting profile for %s", user_id)
            raise ServiceError("Failed to delete profile") from exc

    def update_privacy_settings(self, user_id: UUID, privacy_settings: Dict[str, bool], requesting_user: Optional[User] = None) -> ProfileOut:
        """
        Update privacy settings separately from other profile data.
        """
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to update this profile's privacy settings")

        profile = user_crud.get_profile_by_user_id(self.db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")

        # Validate privacy settings
        valid_keys = {'show_profile', 'show_email', 'show_phone', 'allow_messages', 'allow_media', 'allow_activities', 'allow_journals'}
        if not all(key in valid_keys for key in privacy_settings.keys()):
            invalid_keys = set(privacy_settings.keys()) - valid_keys
            raise ValidationError(f"Invalid privacy setting keys: {invalid_keys}")

        try:
            updated_profile = user_crud.update_profile_privacy(self.db, db_profile=profile, privacy_settings=privacy_settings)
            return updated_profile
        except Exception as exc:
            self.db.rollback()
            logger.exception("Failed updating privacy settings for %s", user_id)
            raise ServiceError("Failed to update privacy settings") from exc

    def search_profiles(self, query: str, skip: int = 0, limit: int = 20, requesting_user: Optional[User] = None) -> List[ProfileOut]:
        """
        Search user profiles with privacy filtering.
        """
        profiles = user_crud.search_profiles(self.db, query=query, skip=skip, limit=limit)
        if not profiles:
            return []
        
        # Apply privacy filtering
        filtered_profiles = []
        for profile in profiles:            
            filtered_profile = self._apply_privacy_filter(profile, requesting_user)
            filtered_profiles.append(filtered_profile)
        
        return filtered_profiles

    def _apply_privacy_filter(self, profile: UserProfile, requesting_user: Optional[User]) -> ProfileOut:
        """
        Apply privacy settings to a profile based on the requesting user.
        """
        if not profile.privacy_settings:
            return profile
        
        if requesting_user and requesting_user.role == UserRole.admin:
            return profile
        
        filtered_data = profile.dict()
        privacy = profile.privacy_settings
        
        for field, allowed in privacy.items():
            if not allowed and field in filtered_data:
                filtered_data[field] = None
                
        return ProfileOut(**filtered_data)

    def _validate_profile_data(self, profile_in: ProfileUpdate) -> None:
        """
        Validate profile data before update.
        """
        if profile_in.primary_pillar_weights:
            total_weight = sum(profile_in.primary_pillar_weights.values())
            if not (0.99 <= total_weight <= 1.01):
                raise ValidationError("Primary pillar weights must sum to 1.0")

        if profile_in.medications:
            required_fields = {'name', 'dosage', 'frequency'}
            for med in profile_in.medications:
                if not all(field in med for field in required_fields):
                    raise ValidationError(f"Medication must contain fields: {required_fields}")