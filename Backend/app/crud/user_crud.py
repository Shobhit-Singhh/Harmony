# app/crud/user_crud.py
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DatabaseError,
    DatabaseConflictError,
    DatabaseNotFoundError,
)
from app.models.user_models import User, UserProfile, UserRole

# -----------------------------
# User CRUD Operations
# -----------------------------


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Retrieve a user by their UUID (active only)."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by email, return None if not found."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """Retrieve a user by phone number."""
    return db.query(User).filter(User.phone_number == phone_number).first()


def create_user(
    db: Session,
    username: str,
    email: str,
    phone_number: Optional[str],
    password_hash: str,
    role: UserRole = UserRole.user,
) -> User:
    """Create a new user record."""
    db_user = User(
        username=username,
        email=email,
        phone_number=phone_number,
        password_hash=password_hash,
        status="active",
        role=role,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        last_login_at=None,
        failed_login_attempts=0,
        lockout_until=None,
        password_changed_at=None,
        onboarding_completed=False,
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while creating user") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while creating user") from e


def update_user(db: Session, db_user: User, updates: Dict) -> User:
    """Update user fields (excluding password)."""
    
    for field, value in updates.items():
        if hasattr(db_user, field):
            setattr(db_user, field, value)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while updating user") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while updating user") from e


def update_user_password(db: Session, db_user: User, password_hash: str) -> User:
    """Update user password hash."""
    
    db_user.password_hash = password_hash
    db_user.password_changed_at = datetime.now(timezone.utc)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while updating password") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while updating password") from e


def update_last_login(db: Session, db_user: User) -> User:
    """Update user's last login timestamp."""
    
    db_user.last_login_at = datetime.now(timezone.utc)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while updating last login") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while updating last login") from e


def status_update(db: Session, db_user: User, status: str) -> User:
    """Update user status (active, banned, suspended, deactivated)."""
    if not db_user:
        raise DatabaseNotFoundError("User not found")
    
    if status not in ["active", "banned", "suspended", "deactivated"]:
        raise ValueError("Invalid status value")

    db_user.status = status
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while updating user status") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while updating user status") from e


def delete_user(
    db: Session, db_user: User, hard_delete: bool = False
) -> bool:
    """Delete user (hard or soft)."""
    if not db_user:
        raise DatabaseNotFoundError("User not found")

    if hard_delete:
        try:
            db.delete(db_user)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            raise DatabaseError("Unexpected database error while deleting user") from e
    else:
        status_update(db, db_user, "deactivated")
        return True