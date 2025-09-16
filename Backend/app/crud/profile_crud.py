# app/crud/profile_crud.py
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DatabaseError,
    DatabaseConflictError,
    DatabaseNotFoundError,
)
from app.models.user_models import UserProfile

# -----------------------------
# Profile CRUD Operations
# -----------------------------


def get_profile_by_user_id(db: Session, user_id: UUID) -> Optional[UserProfile]:
    """Retrieve profile by user ID."""
    return db.query(UserProfile).filter(UserProfile.id == user_id).first()


def create_profile(db: Session, user_id: UUID, profile_create) -> UserProfile:
    """
    Create a new user profile.
    profile_create: Pydantic schema (ProfileCreate).
    Maps schema fields to ORM and returns the ORM instance.
    """
    db_profile = UserProfile(
        id=user_id, **profile_create.model_dump(exclude_unset=True)
    )
    
    try:
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while creating profile") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while creating profile") from e


def update_profile(db: Session, db_profile: UserProfile, profile_update) -> UserProfile:
    """
    Update profile fields from schema.
    profile_update: Pydantic schema (ProfileUpdate).
    Updates profile fields from schema.
    """
    
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_profile, key):
            setattr(db_profile, key, value)

    try:
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while updating profile") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while updating profile") from e


def update_profile_privacy(db: Session, db_profile: UserProfile, privacy_settings: Dict[str, bool]) -> UserProfile:
    """Update profile privacy settings."""

    db_profile.privacy_settings = privacy_settings
    
    try:
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while updating profile privacy") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while updating profile privacy") from e


def delete_profile(db: Session, db_profile: UserProfile, hard_delete: bool = False) -> bool:
    """
    Delete profile (hard or soft).
    - Hard delete: removes the row.
    - Soft delete: anonymizes/clears PII while keeping the row.
    """

    try:
        if hard_delete:
            db.delete(db_profile)
        else:
            # Soft delete: anonymize PII fields
            pii_fields = [
                "full_name", 
                "date_of_birth", 
                "gender", 
                "location", 
                "timezone", 
                "crisis_contact"
            ]
            
            for field in pii_fields:
                if hasattr(db_profile, field):
                    setattr(db_profile, field, None)

            db_profile.privacy_settings = {"show_profile": False}
            db.add(db_profile)

        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while deleting profile") from e