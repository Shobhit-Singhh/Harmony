# app/services/profile_service.py
from __future__ import annotations
from typing import Optional, Dict, Any, List
from uuid import UUID
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user_models import User, UserRole
from app.schemas.user_schema import (
    ProfileCreate,
    ProfileUpdate,
    ProfileOut,
)
from app.core.exceptions import (
    ServiceError,
    NotFoundError,
    ConflictError,
    PermissionError,
    ValidationError,
    DatabaseConflictError,
    DatabaseError,
)
from app.crud import user_crud, profile_crud

logger = logging.getLogger(__name__)


# -----------------------------
# Profile Service
# -----------------------------
class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def create_profile(
        self, 
        user_id: UUID, 
        profile_in: ProfileCreate, 
        requesting_user: Optional[User] = None
    ) -> ProfileOut:
        """Create a new user profile."""
        # Permission checks
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to create profile for this user")

        # Check if user exists
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")

        # Check if profile already exists with content
        existing_profile = profile_crud.get_profile_by_user_id(self.db, user_id)
        if existing_profile and existing_profile.full_name is not None:
            raise ConflictError("Profile already exists")

        try:
            profile = profile_crud.create_profile(
                self.db, 
                user_id=user_id, 
                profile_create=profile_in
            )
            return ProfileOut.model_validate(profile)
        except DatabaseConflictError as e:
            logger.warning("Conflict during profile creation: %s", e)
            raise ConflictError("Profile creation failed due to constraint") from e
        except DatabaseError as e:
            logger.error("Database error during profile creation: %s", e)
            raise ServiceError("Profile creation failed") from e
        except Exception as e:
            logger.exception("Unexpected error during profile creation: %s", e)
            raise ServiceError("Unexpected error during profile creation") from e

    def get_profile(
        self, 
        user_id: UUID, 
        requesting_user: Optional[User] = None
    ) -> ProfileOut:
        """Get user profile with privacy filtering."""
        profile = profile_crud.get_profile_by_user_id(self.db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")

        # Apply privacy filtering if requester is not owner or admin
        filtered_profile = self._apply_privacy_filter(profile, requesting_user)
        return filtered_profile

    def update_profile(
        self, 
        user_id: UUID, 
        profile_in: ProfileUpdate, 
        requesting_user: Optional[User] = None
    ) -> ProfileOut:
        """Update user profile."""
        # Permission checks
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to update this profile")

        profile = profile_crud.get_profile_by_user_id(self.db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")

        # Validate profile data
        self._validate_profile_data(profile_in)

        try:
            updated_profile = profile_crud.update_profile(
                self.db, 
                db_profile=profile, 
                profile_update=profile_in
            )
            return ProfileOut.model_validate(updated_profile)
        except DatabaseConflictError as e:
            logger.warning("Conflict during profile update: %s", e)
            raise ConflictError("Profile update failed due to constraint") from e
        except DatabaseError as e:
            logger.error("Database error during profile update: %s", e)
            raise ServiceError("Profile update failed") from e
        except Exception as e:
            logger.exception("Unexpected error during profile update: %s", e)
            raise ServiceError("Unexpected error during profile update") from e

    def update_profile_privacy(
        self, 
        user_id: UUID, 
        privacy_settings: Dict[str, bool], 
        requesting_user: Optional[User] = None
    ) -> ProfileOut:
        """Update profile privacy settings."""
        # Permission checks
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to update privacy settings")

        profile = profile_crud.get_profile_by_user_id(self.db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")

        # Validate privacy settings
        self._validate_privacy_settings(privacy_settings)

        try:
            updated_profile = profile_crud.update_profile_privacy(
                self.db, 
                db_profile=profile, 
                privacy_settings=privacy_settings
            )
            return ProfileOut.model_validate(updated_profile)
        except DatabaseConflictError as e:
            logger.warning("Conflict during privacy update: %s", e)
            raise ConflictError("Privacy settings update failed") from e
        except DatabaseError as e:
            logger.error("Database error during privacy update: %s", e)
            raise ServiceError("Privacy settings update failed") from e

    def delete_profile(
        self, 
        user_id: UUID, 
        hard_delete: bool = False, 
        requesting_user: Optional[User] = None
    ) -> bool:
        """Delete user profile (soft or hard delete)."""
        # Permission checks
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to delete this profile")

        profile = profile_crud.get_profile_by_user_id(self.db, user_id)
        if not profile:
            raise NotFoundError("Profile not found")

        try:
            return profile_crud.delete_profile(self.db, profile, hard_delete)
        except DatabaseError as e:
            logger.error("Database error during profile deletion: %s", e)
            raise ServiceError("Failed to delete profile") from e
        except Exception as e:
            logger.exception("Unexpected error during profile deletion: %s", e)
            raise ServiceError("Failed to delete profile") from e

    # -----------------------------
    # Helper Methods
    # -----------------------------
    def _apply_privacy_filter(
        self, 
        profile, 
        requesting_user: Optional[User] = None
    ) -> ProfileOut:
        """Apply privacy filtering to profile based on requesting user."""
        # If requesting user is the owner or an admin, return full profile
        if requesting_user and (
            requesting_user.id == profile.id or 
            requesting_user.role == UserRole.admin
        ):
            return ProfileOut.model_validate(profile)

        # Apply privacy filtering based on profile settings
        profile_data = ProfileOut.model_validate(profile).model_dump()
        
        if hasattr(profile, 'privacy_settings') and profile.privacy_settings:
            privacy_settings = profile.privacy_settings
            
            # Filter sensitive fields based on privacy settings
            if not privacy_settings.get("show_profile", True):
                # Hide most profile information
                filtered_fields = {
                    "id": profile_data["id"],
                    "full_name": None,
                    "bio": None,
                    "location": None,
                    "date_of_birth": None,
                    "gender": None,
                    "timezone": None,
                    "crisis_contact": None,
                    "privacy_settings": {"show_profile": False}
                }
                return ProfileOut(**filtered_fields)
        
        return ProfileOut.model_validate(profile)

    def _validate_profile_data(self, profile_data: ProfileUpdate) -> None:
        """Validate profile data before update."""
        if not profile_data:
            raise ValidationError("No profile data provided")

        # Add specific validation rules as needed
        update_dict = profile_data.model_dump(exclude_unset=True)
        
        # Example validations
        if "date_of_birth" in update_dict and update_dict["date_of_birth"]:
            # Could add age validation, future date checks, etc.
            pass
        
        if "bio" in update_dict and update_dict["bio"]:
            if len(update_dict["bio"]) > 500:  # Example limit
                raise ValidationError("Bio must be 500 characters or less")

    def _validate_privacy_settings(self, privacy_settings: Dict[str, bool]) -> None:
        """Validate privacy settings structure."""
        if not isinstance(privacy_settings, dict):
            raise ValidationError("Privacy settings must be a dictionary")
        
        allowed_settings = {
            "show_profile",
            "show_email", 
            "show_phone",
            "show_location",
            "show_birthday"
        }
        
        for key, value in privacy_settings.items():
            if key not in allowed_settings:
                raise ValidationError(f"Invalid privacy setting: {key}")
            if not isinstance(value, bool):
                raise ValidationError(f"Privacy setting {key} must be boolean")