# app/services/auth_service.py
from __future__ import annotations
from typing import Optional, Tuple, Union, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta, timezone
import logging

from jose import jwt, JWTError
from jwt.exceptions import PyJWTError, ExpiredSignatureError, InvalidSignatureError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    ServiceError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
    DatabaseError,
)
from app.models.user_models import User
from app.crud.user_crud import get_user_by_email, get_user_by_id
from app.crud.auth_crud import (
    update_last_login,
    increment_failed_attempts,
    reset_failed_attempts,
    set_lockout_until,
    clear_lockout,
    update_password_changed_at,
)
from app.schemas.user_schema import UserOut, UserOutwithPassword

logger = logging.getLogger(__name__)

# -----------------------------
# Security Setup
# -----------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -----------------------------
# Auth Service
# -----------------------------
class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and return tokens.
        Returns: Dict containing access_token, refresh_token, token_type, and user info
        """
        user = get_user_by_email(self.db, email=email)
        if not user:
            raise UnauthorizedError("Invalid email or password")

        # Check account lockout
        now = datetime.now(timezone.utc)
        if user.lockout_until and user.lockout_until > now:
            raise UnauthorizedError("Account is locked. Try again later.")

        # Verify password
        if not self.verify_password(password, user.password_hash):
            try:
                increment_failed_attempts(self.db, user)
                if user.failed_login_attempts >= 5:  # configurable threshold
                    lockout_time = now + timedelta(minutes=15)
                    set_lockout_until(self.db, user, lockout_time)
            except DatabaseError as e:
                logger.error("Failed to update login attempts: %s", e)
            raise UnauthorizedError("Invalid email or password")

        # Successful login: reset failed attempts and update last login
        try:
            reset_failed_attempts(self.db, user)
            update_last_login(self.db, user)
        except DatabaseError as e:
            logger.error("Failed to update login status: %s", e)

        # Issue tokens
        payload = {
            "sub": str(user.id), 
            "email": user.email
            } 
        
        access_token = self.create_access_token(payload)
        refresh_token = self.create_refresh_token(payload)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserOut.model_validate(user)
        }
    
    def validate_token_issue_time(self, token_payload: Dict[str, Any], user: User, token_issue_time: datetime) -> bool:
        """Validate token issue time against user's password change time."""
        if user.password_changed_at:
            # Ensure both datetimes are timezone-aware
            password_changed_at = user.password_changed_at
            if password_changed_at.tzinfo is None:
                # If stored as naive, assume it's UTC
                password_changed_at = password_changed_at.replace(tzinfo=timezone.utc)
            
            if token_issue_time < password_changed_at:
                return False
        return True
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh access token using refresh token.
        Returns: Dict containing new access_token (and optionally new refresh_token if rotating).
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.REFRESH_SECRET_KEY,   # <-- match the create_refresh_token secret
                algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise UnauthorizedError("Invalid refresh token")
        except ExpiredSignatureError:
            raise UnauthorizedError("Refresh token has expired")
        except (JWTError, PyJWTError):
            raise UnauthorizedError("Invalid refresh token 2")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid refresh token")

        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise ValidationError("Invalid user ID in token")

        user = get_user_by_id(self.db, user_uuid)
        if not user:
            raise NotFoundError("User not found")

        token_iat = payload.get("iat")
        if not token_iat:
            raise UnauthorizedError("Token revoked due to password change")
        
        if not self.validate_token_issue_time(payload, user, token_issue_time=datetime.fromtimestamp(token_iat, tz=timezone.utc)):
            raise UnauthorizedError("Token revoked due to password change")
        
        # Issue new tokens
        new_payload = {"sub": str(user.id), "email": user.email}
        access_token = self.create_access_token(new_payload)

        # Optionally rotate refresh token:
        # refresh_token = self.create_refresh_token(new_payload)

        return {
            "access_token": access_token,
            # "refresh_token": refresh_token  # if rotating
        }

    def change_password(self, user_id: Union[str, UUID], new_password: str) -> UserOut:
        """Change user password and invalidate existing tokens."""
        # Ensure UUID type
        if isinstance(user_id, str):
            try:
                user_uuid = UUID(user_id)
            except ValueError:
                raise ValidationError("Invalid user ID format")
        else:
            user_uuid = user_id

        user = get_user_by_id(self.db, user_uuid)
        if not user:
            raise NotFoundError("User not found")

        try:
            # Hash new password and update
            hashed_pw = self.hash_password(new_password)
            user.password_hash = hashed_pw
            update_password_changed_at(self.db, user)
            return UserOut.model_validate(user)
        except DatabaseError as e:
            logger.error("Failed to change password for user %s: %s", user_id, e)
            raise ServiceError("Failed to change password") from e

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        Returns: Token payload
        """
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id_str = payload.get("sub")
            
            if not get_user_by_id(self.db, UUID(user_id_str)):
                raise UnauthorizedError("Invalid authentication token")
            return payload
        except ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except (JWTError, PyJWTError):
            raise UnauthorizedError("Invalid token")

    def get_current_user_from_token(self, token: str) -> UserOut:
        """Get current user from JWT token."""
        payload = self.verify_token(token)
        user_id_str = payload.get("sub")

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise ValidationError("Malformed user ID in token")

        user = get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")

        return UserOut.model_validate(user)

    def get_current_user_with_password_from_token(self, token: str) -> UserOutwithPassword:
        """Get current user with password hash from JWT token."""
        payload = self.verify_token(token)
        user_id_str = payload.get("sub")

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise ValidationError("Malformed user ID in token")

        user = get_user_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")

        return UserOutwithPassword.model_validate(user)
    # -----------------------------
    # Helper Methods
    # -----------------------------
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(days=7)
        )
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        })
        return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_password(plain_password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, password_hash)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
