# app/services/user_service.py
from __future__ import annotations
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user_models import User, UserRole
from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserOut,
    ProfileCreate,
    ProfileOut,
    UserWithProfileOut,
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
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class UserState(str, Enum):
    """User account states."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"


# -----------------------------
# User Service
# -----------------------------
class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_in: UserCreate) -> UserWithProfileOut:
        """Create a new user with profile."""
        # Check for existing email
        if user_crud.get_user_by_email(self.db, email=user_in.email):
            raise ConflictError("Email already registered")
        
        # Check for existing phone number
        if user_in.phone_number and user_crud.get_user_by_phone(self.db, phone_number=user_in.phone_number):
            raise ConflictError("Phone number already registered")

        # Hash password
        hashed_pw = AuthService.hash_password(user_in.password)

        try:
            # Create user
            db_user = user_crud.create_user(
                self.db,
                email=user_in.email,
                password_hash=hashed_pw,
                phone_number=user_in.phone_number,
                username=user_in.username,
                role=getattr(user_in, "role", UserRole.user),
            )

            # Create basic profile
            profile = profile_crud.create_profile(
                self.db, 
                user_id=db_user.id, 
                profile_create=ProfileCreate()
            )

            # Build response
            user_dict = UserOut.model_validate(db_user).model_dump()
            user_dict["profile"] = (
                ProfileOut.model_validate(profile).model_dump() 
                if profile else None
            )

            return UserWithProfileOut(**user_dict)

        except DatabaseConflictError as e:
            logger.warning("Conflict in user creation: %s", e)
            raise ConflictError("User already exists") from e
        except DatabaseError as e:
            logger.error("Database error during user creation: %s", e)
            raise ServiceError("Failed to create user") from e
        except Exception as e:
            logger.exception("Unexpected error during user creation: %s", e)
            raise ServiceError("Unexpected error while creating user") from e

    def get_user_by_id(
        self, 
        user_id: UUID, 
        requesting_user: Optional[User] = None
    ) -> UserOut:
        """Get user by ID with permission checks."""
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")
        
        if requesting_user is None:
            raise PermissionError("Authentication required")
        
        # Permission checks
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to view this user")

        return UserOut.model_validate(user)

    def get_user_with_profile(
        self, 
        user_id: UUID, 
        requesting_user: Optional[User] = None
    ) -> UserWithProfileOut:
        """Get user with profile information."""
        user_schema = self.get_user_by_id(user_id, requesting_user)
        profile = profile_crud.get_profile_by_user_id(self.db, user_id)
        
        user_dict = user_schema.model_dump()
        user_dict["profile"] = (
            ProfileOut.model_validate(profile).model_dump() 
            if profile else None
        )
        
        return UserWithProfileOut(**user_dict)

    def get_user_by_email(self, email: str) -> Optional[UserOut]:
        """Get user by email address."""
        user = user_crud.get_user_by_email(self.db, email)
        return UserOut.model_validate(user) if user else None

    def update_user(
        self, 
        user_id: UUID, 
        user_update: UserUpdate, 
        requesting_user: Optional[User] = None
    ) -> UserOut:
        """Update user information."""
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")
        
        if requesting_user is None:
            raise PermissionError("Authentication required")
        
        # Permission checks
        if requesting_user and requesting_user.id != user_id:
            if requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to update this user")

        try:
            update_data = user_update.model_dump(exclude_unset=True)
            updated_user = user_crud.update_user(self.db, user, update_data)
            return UserOut.model_validate(updated_user)
        except DatabaseConflictError as e:
            logger.warning("Conflict during user update: %s", e)
            raise ConflictError("Update conflict occurred") from e
        except DatabaseError as e:
            logger.error("Database error during user update: %s", e)
            raise ServiceError("Failed to update user") from e

    def update_user_status(
        self, 
        user_id: UUID, 
        status: str, 
        requesting_user: Optional[User] = None
    ) -> UserOut:
        """Update user account status."""
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")

        # Only admins can change user status
        if requesting_user and requesting_user.role != UserRole.admin:
            raise PermissionError("Not authorized to change user status")

        if status not in [state.value for state in UserState]:
            raise ValidationError(f"Invalid status: {status}")

        try:
            updated_user = user_crud.status_update(self.db, user, status)
            return UserOut.model_validate(updated_user)
        except DatabaseError as e:
            logger.error("Database error during status update: %s", e)
            raise ServiceError("Failed to update user status") from e

    def delete_user(
        self, 
        user_id: UUID, 
        hard_delete: bool = False, 
        requesting_user: Optional[User] = None
    ) -> bool:
        """Delete user account (soft or hard delete)."""
        user = user_crud.get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")

        # Permission checks
        if requesting_user:
            if requesting_user.id != user_id and requesting_user.role != UserRole.admin:
                raise PermissionError("Not authorized to delete this user")

        try:
            return user_crud.delete_user(self.db, user, hard_delete)
        except DatabaseError as e:
            logger.error("Database error during user deletion: %s", e)
            raise ServiceError("Failed to delete user") from e

    def list_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        requesting_user: Optional[User] = None
    ) -> List[UserOut]:
        """List users (admin only)."""
        if requesting_user and requesting_user.role != UserRole.admin:
            raise PermissionError("Not authorized to list users")

        try:
            # This would need to be implemented in user_crud
            # users = user_crud.get_users(self.db, skip=skip, limit=limit)
            # return [UserOut.model_validate(user) for user in users]
            raise NotImplementedError("User listing not implemented")
        except DatabaseError as e:
            logger.error("Database error during user listing: %s", e)
            raise ServiceError("Failed to list users") from e

    def search_users(
        self, 
        query: str, 
        requesting_user: Optional[User] = None
    ) -> List[UserOut]:
        """Search users by username or email (admin only)."""
        if requesting_user and requesting_user.role != UserRole.admin:
            raise PermissionError("Not authorized to search users")

        try:
            # This would need to be implemented in user_crud
            # users = user_crud.search_users(self.db, query=query)
            # return [UserOut.model_validate(user) for user in users]
            raise NotImplementedError("User search not implemented")
        except DatabaseError as e:
            logger.error("Database error during user search: %s", e)
            raise ServiceError("Failed to search users") from e

def out():
# def list_users(
#     self,
#     skip: int = 0,
#     limit: int = 100,
#     filters: Optional[Dict[str, Any]] = None,
#     requesting_user: Optional[User] = None,
# ) -> List[UserOut]:
#     if requesting_user and requesting_user.role != UserRole.admin:
#         raise PermissionError("Not authorized to list users")

#     orm_users = user_crud.list_users(self.db, skip=skip, limit=limit, filters=filters)
#     return [UserOut.model_validate(u) for u in orm_users]

# def update_user(
#     self,
#     user_id: UUID,
#     user_in: UserUpdate,
#     requesting_user: Optional[User] = None,
# ) -> UserOut:
#     user = user_crud.get_user_by_id(self.db, user_id)
#     if not user:
#         raise NotFoundError("User not found")
        
#     if requesting_user is None:
#         raise PermissionError("Authentication required")
        
#     if requesting_user and requesting_user.id != user_id:
#         if requesting_user.role != UserRole.admin:
#             raise PermissionError("Not authorized to update this user")

#     if user_in.role and (not requesting_user or requesting_user.role != UserRole.admin):
#         raise PermissionError("Only admins can change user roles")

#     try:
#         updated_user = user_crud.update_user(self.db, db_user=user, updates=user_in.model_dump(exclude_unset=True))
#         return UserOut.model_validate(updated_user)

#     except IntegrityError as e:
#         self.db.rollback()
#         logger.exception("Integrity error during user update: %s", e)
#         raise DatabaseConflictError("User update failed due to constraint") from e
#     except Exception as e:
#         self.db.rollback()
#         logger.exception("Unexpected error during user update: %s", e)
#         raise DatabaseError("Unexpected database error during user update") from e

# def change_password(
#     self,
#     user_id: UUID,
#     old_password: str,
#     new_password: str,
#     requesting_user: Optional[User] = None,
# ) -> None:
#     user = user_crud.get_user_by_id(self.db, user_id)
#     if not user:
#         raise NotFoundError("User not found")
                
        # if requesting_user is None:
        #     raise PermissionError("Authentication required")
        
#     if requesting_user and requesting_user.id != user_id:
#         if requesting_user.role != UserRole.admin:
#             raise PermissionError("Not authorized to change this user's password")

#     if not (requesting_user and requesting_user.role == UserRole.admin):
#         if not security.verify_password(old_password, user.password_hash):
#             raise ValidationError("Old password is incorrect")

#     new_hashed_pw = security.get_password_hash(new_password)

#     try:
#         # pass db_user to CRUD (signature: update_user_password(db, db_user, password_hash))
#         user_crud.update_user_password(self.db, db_user=user, password_hash=new_hashed_pw)
#     except IntegrityError as e:
#         self.db.rollback()
#         logger.exception("Integrity error during password change: %s", e)
#         raise DatabaseConflictError("Password change failed due to constraint") from e
#     except Exception as e:
#         self.db.rollback()
#         logger.exception("Unexpected error during password change: %s", e)
#         raise DatabaseError("Unexpected database error during password change") from e

# def change_user_state(
#     self,
#     user_id: UUID,
#     target_state: UserState,
#     requesting_user: Optional[User],
# ) -> UserOut:
#     user = user_crud.get_user_by_id(self.db, user_id)
#     if not user:
#         raise NotFoundError("User not found")

#     if requesting_user and requesting_user.id == user_id and requesting_user.role != UserRole.admin:
#         if target_state not in {UserState.ACTIVE, UserState.DEACTIVATED}:
#             raise PermissionError("Users can only activate/deactivate their own account")
        
        # if requesting_user is None:
        #     raise PermissionError("Authentication required")
        
#     if requesting_user and requesting_user.id != user_id:
#         if requesting_user.role != UserRole.admin:
#             raise PermissionError("Not authorized to manage other users")

#     try:
#         updated_user = user_crud.update_user_state(self.db, user_id=user_id, target_state=target_state)
#         return UserOut.model_validate(updated_user)
#     except Exception as e:
#         self.db.rollback()
#         logger.exception("Unexpected error during user state change for %s: %s", user_id, e)
#         raise DatabaseError("Unexpected database error during user state change") from e

# # ---------- Profile operations ----------

# def update_privacy_settings(self, user_id: UUID, privacy_settings: Dict[str, bool], requesting_user: Optional[User] = None) -> ProfileOut:
#         
        # if requesting_user is None:
        #     raise PermissionError("Authentication required")
            
# if requesting_user and requesting_user.id != user_id:
#         if requesting_user.role != UserRole.admin:
#             raise PermissionError("Not authorized to update this profile's privacy settings")

#     profile = user_crud.get_profile_by_user_id(self.db, user_id)
#     if not profile:
#         raise NotFoundError("Profile not found")

#     valid_keys = {'show_profile', 'show_email', 'show_phone', 'allow_messages', 'allow_media', 'allow_activities', 'allow_journals'}
#     invalid_keys = set(privacy_settings.keys()) - valid_keys
#     if invalid_keys:
#         raise ValidationError(f"Invalid privacy setting keys: {invalid_keys}")

#     try:
#         updated_profile = user_crud.update_profile_privacy(self.db, db_profile=profile, privacy_settings=privacy_settings)
#         return ProfileOut.model_validate(updated_profile)
#     except Exception as exc:
#         self.db.rollback()
#         logger.exception("Failed updating privacy settings for %s: %s", user_id, exc)
#         raise ServiceError("Failed to update privacy settings") from exc

# def search_profiles(self, query: str, skip: int = 0, limit: int = 20, requesting_user: Optional[User] = None) -> List[ProfileOut]:
#     profiles = user_crud.search_profiles(self.db, query=query, skip=skip, limit=limit)
#     if not profiles:
#         return []

#     filtered_profiles: List[ProfileOut] = []
#     for profile in profiles:
#         filtered = self._apply_privacy_filter(profile, requesting_user)
#         filtered_profiles.append(filtered)

#     return filtered_profiles

# def _apply_privacy_filter(self, profile: UserProfile, requesting_user: Optional[User]) -> ProfileOut:
#     """
#     Apply privacy settings to a profile based on the requesting user and return ProfileOut schema.
#     Admins and the profile owner see full profile.
#     """
#     if not profile:
#         raise NotFoundError("Profile not found")

#     # Owners and admins see everything
#     if requesting_user and (requesting_user.role == UserRole.admin or requesting_user.id == profile.id):
#         return ProfileOut.model_validate(profile)

#     # If no privacy settings, return public representation (ProfileOut will decide fields)
#     privacy = profile.privacy_settings or {}
#     # Convert ORM -> dict via Pydantic model_dump
#     profile_data = ProfileOut.model_validate(profile).model_dump()

#     # Fields used in privacy settings are expected keys, but privacy may contain finer-grained flags.
#     # If a privacy key is False, remove that field from the response (set to None).
#     for key, allowed in privacy.items():
#         # privacy keys might be like 'show_profile' or 'show_email' — map them to profile fields
#         if not allowed:
#             # simple mapping rules, expand if you have more privacy keys
#             if key == "show_profile":
#                 # hide most PII fields
#                 for pii in ["full_name", "date_of_birth", "gender", "location", "timezone"]:
#                     if pii in profile_data:
#                         profile_data[pii] = None
#             elif key == "show_email":
#                 profile_data.pop("email", None)  # if email is included in profile schema
#             elif key == "show_phone":
#                 profile_data.pop("phone_number", None)
#             else:
#                 # if privacy key directly matches a profile field, null it
#                 if key in profile_data:
#                     profile_data[key] = None

#     return ProfileOut(**profile_data)

# def _validate_profile_data(self, profile_in: ProfileUpdate) -> None:
#     """
#     Validate profile data before update.
#     """
#     if profile_in.primary_pillar_weights:
#         total_weight = sum(profile_in.primary_pillar_weights.values())
#         if not (0.99 <= total_weight <= 1.01):
#             raise ValidationError("Primary pillar weights must sum to 1.0")

#     if profile_in.medications:
#         required_fields = {'name', 'dosage', 'frequency'}
#         for med in profile_in.medications:
#             if not all(field in med for field in required_fields):
#                 raise ValidationError(f"Medication must contain fields: {required_fields}")
    pass