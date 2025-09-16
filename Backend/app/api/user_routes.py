# app/api/user_routes.py
"""
Complete FastAPI routes for user management.
This module provides all user-related API endpoints with proper error handling,
authentication, authorization, and comprehensive documentation.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from functools import wraps
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.services.user_service import UserService, UserState
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService
from app.core.config import get_db
from app.core.exceptions import (
    ServiceError,
    NotFoundError,
    ConflictError,
    PermissionError,
    ValidationError,
    UnauthorizedError,
)
from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserOut,
    ProfileUpdate,
    ProfileOut,
    UserWithProfileOut,
    UserRole,
)
from app.models.user_models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/users", tags=["users"])
security = HTTPBearer()

# -----------------------------
# Request/Response Schemas
# -----------------------------

class MessageResponse(BaseModel):
    """Standard message response schema."""
    message: str = Field(..., description="Response message")
    success: bool = True

class LoginRequest(BaseModel):
    """Login request schema."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")

class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="Valid refresh token")

class TokenResponse(BaseModel):
    """Authentication token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserOut] = None

class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

class AdminPasswordChangeRequest(BaseModel):
    """Admin password change request schema."""
    user_id: UUID = Field(..., description="Target user ID")
    new_password: str = Field(..., min_length=8, description="New password")

class StatusChangeRequest(BaseModel):
    """User status change request schema."""
    status: UserState = Field(..., description="New user status")
    reason: Optional[str] = Field(None, description="Reason for status change")

class PrivacySettingsRequest(BaseModel):
    """Privacy settings update request schema."""
    show_profile: Optional[bool] = None
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None
    show_location: Optional[bool] = None
    show_birthday: Optional[bool] = None

# -----------------------------
# Dependencies
# -----------------------------

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get user service dependency."""
    return UserService(db)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get auth service dependency."""
    return AuthService(db)

def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    """Get profile service dependency."""
    return ProfileService(db)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user."""
    try:
        user = auth_service.get_current_user_from_token(credentials.credentials)
        return user
    except Exception as e:
        logger.warning("Authentication failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_secret(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user with password hash."""
    try:
        user = auth_service.get_current_user_with_password_from_token(credentials.credentials)
        return user
    except Exception as e:
        logger.warning("Authentication failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    
    
    
# -----------------------------
# Exception Handler Decorator
# -----------------------------

def handle_service_exceptions(func):
    """Decorator to handle service exceptions and convert to HTTP exceptions."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except UnauthorizedError as e:
            logger.warning("Unauthorized access: %s", e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        except PermissionError as e:
            logger.warning("Permission denied: %s", e)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except NotFoundError as e:
            logger.info("Resource not found: %s", e)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except ConflictError as e:
            logger.warning("Conflict error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except ValidationError as e:
            logger.warning("Validation error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
        except ServiceError as e:
            logger.error("Service error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    return wrapper

# -----------------------------
# Authentication Routes
# -----------------------------

@router.post(
    "/register",
    response_model=UserWithProfileOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account with automatic profile creation."
)
@handle_service_exceptions
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user account."""
    return user_service.create_user(user_data)

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return JWT tokens."
)
@handle_service_exceptions
async def login_user(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user with email and password."""
    result = auth_service.login(login_data.email, login_data.password)
    return TokenResponse(**result)

@router.post(
    "/refresh",
    response_model=Dict[str, str],
    summary="Refresh access token",
    description="Get new access token using refresh token."
)
@handle_service_exceptions
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token."""
    return auth_service.refresh_token(refresh_data.refresh_token)

# -----------------------------
# Current User Routes
# -----------------------------

@router.get(
    "/me",
    response_model=UserWithProfileOut,
    summary="Get current user info",
    description="Get current authenticated user with profile information."
)
@handle_service_exceptions
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user information with profile."""
    return user_service.get_user_with_profile(current_user.id, current_user)

@router.put(
    "/me",
    response_model=UserOut,
    summary="Update current user",
    description="Update current authenticated user's account information."
)
@handle_service_exceptions
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update current user information."""
    return user_service.update_user(current_user.id, user_update, current_user)

@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change current user's password."
)
@handle_service_exceptions
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user_secret),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change current user's password."""
    # Verify old password first
    print("done till here")
    if not auth_service.verify_password(password_data.old_password, current_user.password_hash):
        return MessageResponse(message="Current password is incorrect", success=False)
    
    auth_service.change_password(current_user.id, password_data.new_password)
    return MessageResponse(message="Password changed successfully")

@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Deactivate account",
    description="Deactivate current user's account (soft delete)."
)
@handle_service_exceptions
async def deactivate_current_user(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate current user account."""
    user_service.delete_user(current_user.id, hard_delete=False, requesting_user=current_user)
    return MessageResponse(message="Account deactivated successfully")

# -----------------------------
# Profile Routes
# -----------------------------

@router.get(
    "/me/profile",
    response_model=ProfileOut,
    summary="Get current user profile",
    description="Get current user's profile information."
)
@handle_service_exceptions
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get current user's profile."""
    return profile_service.get_profile(current_user.id, current_user)

@router.put(
    "/me/profile",
    response_model=ProfileOut,
    summary="Update current user profile",
    description="Update current user's profile information."
)
@handle_service_exceptions
async def update_current_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update current user's profile."""
    return profile_service.update_profile(current_user.id, profile_update, current_user)

@router.patch(
    "/me/profile/privacy",
    response_model=ProfileOut,
    summary="Update privacy settings",
    description="Update current user's profile privacy settings."
)
@handle_service_exceptions
async def update_privacy_settings(
    privacy_settings: PrivacySettingsRequest,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update privacy settings for current user."""
    settings_dict = privacy_settings.dict(exclude_unset=True)
    return profile_service.update_profile_privacy(current_user.id, settings_dict, current_user)

@router.delete(
    "/me/profile",
    response_model=MessageResponse,
    summary="Delete current user profile",
    description="Delete current user's profile (anonymize data)."
)
@handle_service_exceptions
async def delete_current_user_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Delete current user's profile."""
    profile_service.delete_profile(current_user.id, hard_delete=False, requesting_user=current_user)
    return MessageResponse(message="Profile deleted successfully")

# -----------------------------
# Admin Routes
# -----------------------------

@router.get(
    "/{user_id}",
    response_model=UserWithProfileOut,
    summary="Get user by ID (Admin)",
    description="Get any user's information by ID. Admin access required."
)
@handle_service_exceptions
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID (admin only)."""
    return user_service.get_user_with_profile(user_id, current_user)

@router.put(
    "/{user_id}",
    response_model=UserOut,
    summary="Update user by ID (Admin)",
    description="Update any user's information by ID. Admin access required."
)
@handle_service_exceptions
async def update_user_by_id(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update user by ID (admin only)."""
    return user_service.update_user(user_id, user_update, current_user)

@router.patch(
    "/{user_id}/status",
    response_model=UserOut,
    summary="Change user status (Admin)",
    description="Change user account status. Admin access required."
)
@handle_service_exceptions
async def change_user_status(
    user_id: UUID,
    status_data: StatusChangeRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Change user status (admin only)."""
    return user_service.update_user_status(user_id, status_data.status.value, current_user)

@router.post(
    "/{user_id}/reset-password",
    response_model=MessageResponse,
    summary="Reset user password (Admin)",
    description="Reset any user's password. Admin access required."
)
@handle_service_exceptions
async def admin_reset_password(
    user_id: UUID,
    password_data: AdminPasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset user password (admin only)."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    auth_service.change_password(password_data.user_id, password_data.new_password)
    return MessageResponse(message="Password reset successfully")

@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    summary="Delete user (Admin)",
    description="Delete user account. Admin access required."
)
@handle_service_exceptions
async def delete_user_by_id(
    user_id: UUID,
    hard_delete: bool = Query(False, description="Perform hard delete"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Delete user by ID (admin only)."""
    user_service.delete_user(user_id, hard_delete, current_user)
    delete_type = "permanently deleted" if hard_delete else "deactivated"
    return MessageResponse(message=f"User {delete_type} successfully")

@router.get(
    "/",
    response_model=List[UserOut],
    summary="List users (Admin)",
    description="Get paginated list of users. Admin access required."
)
@handle_service_exceptions
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """List users with pagination (admin only)."""
    return user_service.list_users(skip, limit, current_user)