# app/crud/auth_crud.py
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    DatabaseError,
    DatabaseConflictError,
    DatabaseNotFoundError,
)
from app.models.user_models import User

# -----------------------------
# Auth CRUD Operations
# -----------------------------


def update_last_login(db: Session, db_user: User) -> User:
    """Update user's last login timestamp."""
    if not db_user:
        raise DatabaseNotFoundError("User not found")
    
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


def increment_failed_attempts(db: Session, db_user: User) -> User:
    """Increment user's failed login attempts counter."""
    if not db_user:
        raise DatabaseNotFoundError("User not found")
    
    db_user.failed_login_attempts += 1
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while incrementing failed attempts") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while incrementing failed attempts") from e


def reset_failed_attempts(db: Session, db_user: User) -> User:
    """Reset user's failed login attempts counter to zero."""
    if not db_user:
        raise DatabaseNotFoundError("User not found")
    
    db_user.failed_login_attempts = 0
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while resetting failed attempts") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while resetting failed attempts") from e


def set_lockout_until(db: Session, db_user: User, until: datetime) -> User:
    """Set user lockout until specified datetime."""
    if not db_user:
        raise DatabaseNotFoundError("User not found")
    
    db_user.lockout_until = until
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while setting lockout time") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while setting lockout time") from e


def clear_lockout(db: Session, db_user: User) -> User:
    """Clear user lockout by setting lockout_until to None."""
    if not db_user:
        raise DatabaseNotFoundError("User not found")
    
    db_user.lockout_until = None
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while clearing lockout") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while clearing lockout") from e


def update_password_changed_at(db: Session, db_user: User) -> User:
    """Update user's password changed timestamp."""
    if not db_user:
        raise DatabaseNotFoundError("User not found")
    
    db_user.password_changed_at = datetime.now(timezone.utc)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseConflictError("Conflict occurred while updating password timestamp") from e
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseError("Unexpected database error while updating password timestamp") from e