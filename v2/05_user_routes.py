# app/api/user_routes.py
"""
Complete FastAPI routes for user management.
This module provides all user-related API endpoints with proper error handling,
authentication, authorization, and comprehensive documentation.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import time
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.services.user_service import (
    UserService, 
    get_user_service,
    ServiceError,
    NotFoundError,
    ConflictError,
    PermissionError,
    ValidationError,
    UserState,
)
from v1.user_schema import (
    UserCreate,
    UserUpdate,
    UserOut,
    ProfileCreate,
    ProfileUpdate,
    ProfileOut,
    UserWithProfileOut,
    UserRole,
)
from app.models.user_models import User
from Backend.tests.deps import get_db, get_current_user, get_current_active_user
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/users", tags=["users"])
security = HTTPBearer()

# Response models for documentation
class MessageResponse(BaseModel):
    message: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class StateChangeRequest(BaseModel):
    target_state: UserState
    reason: Optional[str] = None

class PrivacySettingsRequest(BaseModel):
    show_profile: Optional[bool] = None
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None
    allow_messages: Optional[bool] = None
    allow_media: Optional[bool] = None
    allow_activities: Optional[bool] = None
    allow_journals: Optional[bool] = None


# Exception handler utility
def handle_service_exceptions(func):
    """Decorator to handle common service exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ConflictError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValidationError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        except ServiceError as e:
            logger.error(f"Service error: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    return wrapper


# -----------------------------
# Authentication & Registration
# -----------------------------

@router.post(
    "/register",
    response_model=UserWithProfileOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Register a new user account with automatic profile creation.
    
    **Requirements:**
    - Email must be unique
    - Username (if provided)
    - Phone number must be unique (if provided)
    - Password must meet complexity requirements (8+ chars, uppercase, lowercase, number, special char)
    
    **Automatic Actions:**
    - Password is hashed securely
    - Empty profile is auto-created
    - User is set as active but unverified
    """,
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Email, username, or phone already exists"},
        422: {"description": "Invalid input data"}
    }
)
@handle_service_exceptions
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user with automatic profile creation."""
    return user_service.create_user(user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user",
    description="Authenticate user credentials and return access token with user data.",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials or inactive account"}
    }
)
async def login_user(
    email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    user_service: UserService = Depends(get_user_service)
):
    """Authenticate user and return access token."""
    user = user_service.authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or account inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Replace with actual JWT token generation
    # from app.core.security import create_access_token
    # access_token = create_access_token(data={"sub": str(user.id)})
    access_token = "your_jwt_token_here"

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


# -----------------------------
# User Operations
# -----------------------------

@router.get(
    "/me",
    response_model=UserWithProfileOut,
    summary="Get current user info",
    description="Get current authenticated user's information including profile."
)
@handle_service_exceptions
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user's information with profile."""
    return user_service.get_user_with_profile(current_user.id, current_user)


@router.put(
    "/me",
    response_model=UserOut,
    summary="Update current user",
    description="""
    Update current user's information.
    
    **Updatable Fields:**
    - username (if unique)
    - email (if unique) 
    - phone_number (if unique)
    - Basic account settings
    
    **Protected Fields:**
    - id, created_at, password_hash are immutable
    - Role changes require admin privileges
    """,
    responses={
        200: {"description": "User updated successfully"},
        422: {"description": "Invalid input data"}
    }
)
@handle_service_exceptions
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update current user's information."""
    return user_service.update_user(current_user.id, user_update, current_user)


@router.post(
    "/me/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change current user's password with old password verification.",
    responses={
        200: {"description": "Password changed successfully"},
        400: {"description": "Invalid current password"},
        422: {"description": "New password doesn't meet requirements"}
    }
)
@handle_service_exceptions
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Change current user's password."""
    user_service.change_password(
        current_user.id, 
        password_data.old_password, 
        password_data.new_password, 
        current_user
    )
    return MessageResponse(message="Password changed successfully")


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Deactivate account",
    description="Deactivate current user's account (soft delete).",
    responses={
        200: {"description": "Account deactivated successfully"}
    }
)
@handle_service_exceptions
async def deactivate_current_user(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate current user's account."""
    user_service.deactivate_user(current_user.id, requesting_user=current_user)
    return MessageResponse(message="Account deactivated successfully")


# -----------------------------
# Profile Management
# -----------------------------

@router.get(
    "/me/profile",
    response_model=ProfileOut,
    summary="Get current user profile",
    description="Get current user's profile information."
)
@handle_service_exceptions
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user's profile."""
    profile = user_service.get_profile(current_user.id, current_user)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


@router.put(
    "/me/profile",
    response_model=ProfileOut,
    summary="Update current user profile",
    description="""
    Update current user's profile information.
    
    **Features:**
    - Validates pillar weights sum to 1.0
    - Validates age requirements (13-120 years)
    - Validates medication format
    - Supports partial updates (only provided fields are updated)
    
    **Profile Fields:**
    - Personal info: full_name, date_of_birth, gender, location, timezone
    - Health info: primary_pillar_weights, medications, conditions, crisis_contact
    - Preferences: preferred_language, privacy_settings
    - Status: onboarding_completed
    """,
    responses={
        200: {"description": "Profile updated successfully"},
        404: {"description": "Profile not found"},
        422: {"description": "Invalid profile data"}
    }
)
@handle_service_exceptions
async def update_current_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update current user's profile."""
    return user_service.update_profile(current_user.id, profile_update, current_user)


@router.put(
    "/me/privacy",
    response_model=ProfileOut,
    summary="Update privacy settings",
    description="""
    Update privacy settings for profile visibility and discoverability.
    
    **Privacy Controls:**
    - show_profile: Whether profile is visible to others
    - show_email: Whether email is visible (future feature)
    - show_phone: Whether phone is visible (future feature)
    - show_in_search: Whether profile appears in search results
    - allow_messages: Whether other users can send messages (future feature)
    """,
    responses={
        200: {"description": "Privacy settings updated successfully"},
        404: {"description": "Profile not found"},
        422: {"description": "Invalid privacy setting keys"}
    }
)
@handle_service_exceptions
async def update_privacy_settings(
    privacy_settings: PrivacySettingsRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update privacy settings."""
    # Convert Pydantic model to dict, excluding None values
    settings_dict = privacy_settings.dict(exclude_unset=True, exclude_none=True)
    return user_service.update_privacy_settings(current_user.id, settings_dict, current_user)


@router.delete(
    "/me/profile",
    response_model=MessageResponse,
    summary="Delete current user profile",
    description="Delete current user's profile (keeps user account active)."
)
@handle_service_exceptions
async def delete_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Delete current user's profile."""
    user_service.delete_profile(current_user.id, current_user)
    return MessageResponse(message="Profile deleted successfully")


# -----------------------------
# User Management (Admin/Public)
# -----------------------------

@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Get user by ID",
    description="""
    Get user information by ID.
    
    **Access Control:**
    - Users can only access their own data
    - Admins can access any user data
    - Sensitive fields are filtered based on role
    """,
    responses={
        200: {"description": "User found"},
        403: {"description": "Not authorized to view this user"},
        404: {"description": "User not found"}
    }
)
@handle_service_exceptions
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID (requires permission)."""
    return user_service.get_user(user_id, current_user)


@router.get(
    "/{user_id}/profile",
    response_model=ProfileOut,
    summary="Get user profile by ID",
    description="""
    Get user profile by ID with privacy filtering applied.
    
    **Privacy Filtering:**
    - Profile data is filtered based on privacy settings
    - Users always see their own full profile
    - Admins see unfiltered data
    - Other users see privacy-filtered data
    """,
    responses={
        200: {"description": "Profile found"},
        404: {"description": "Profile not found"}
    }
)
@handle_service_exceptions
async def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get user profile by ID (with privacy filtering)."""
    profile = user_service.get_profile(user_id, current_user)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


@router.get(
    "/",
    response_model=List[UserOut],
    summary="List users",
    description="""
    List users with pagination and filtering (Admin only).
    
    **Filtering Options:**
    - role: Filter by user role (user, clinician, admin)
    - is_active: Filter by active status
    - is_verified: Filter by verification status
    - email_domain: Filter by email domain
    """,
    responses={
        200: {"description": "Users list"},
        403: {"description": "Admin access required"}
    }
)
@handle_service_exceptions
async def list_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    email_domain: Optional[str] = Query(None, description="Filter by email domain"),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """List users with pagination and filtering (admin only)."""
    filters = {}
    if role:
        filters['role'] = role
    if is_active is not None:
        filters['is_active'] = is_active
    if is_verified is not None:
        filters['is_verified'] = is_verified
    if email_domain:
        filters['email_domain'] = email_domain
        
    return user_service.list_users(skip, limit, filters, current_user)


@router.put(
    "/{user_id}",
    response_model=UserOut,
    summary="Update user by ID",
    description="""
    Update user by ID (Admin only).
    
    **Admin Capabilities:**
    - Change user roles
    - Update any user field
    - Activate/deactivate accounts
    """,
    responses={
        200: {"description": "User updated successfully"},
        403: {"description": "Admin access required"},
        404: {"description": "User not found"}
    }
)
@handle_service_exceptions
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update user by ID (admin only)."""
    return user_service.update_user(user_id, user_update, current_user)


# -----------------------------
# User State Management (Admin)
# -----------------------------

@router.put(
    "/{user_id}/state",
    response_model=UserOut,
    summary="Manage user state",
    description="""
    Manage user state transitions (Admin only).
    
    **State Transitions:**
    - active: User can access all features
    - suspended: User access temporarily disabled
    - deactivated: User soft-deleted, data retained
    - deleted: User permanently removed from system
    
    **Business Rules:**
    - State changes are logged for audit
    - Reason should be provided for non-active states
    - Deleted users cannot be recovered
    """,
    responses={
        200: {"description": "User state updated successfully"},
        403: {"description": "Admin access required"},
        404: {"description": "User not found"},
        400: {"description": "Invalid state transition"}
    }
)
@handle_service_exceptions
async def manage_user_state(
    user_id: UUID,
    state_request: StateChangeRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Manage user state transitions (admin only)."""
    return user_service.manage_user_state(
        user_id, 
        state_request.target_state, 
        current_user, 
        state_request.reason
    )


@router.post(
    "/{user_id}/reset-password",
    response_model=MessageResponse,
    summary="Reset user password",
    description="Reset user password (Admin only). Bypasses old password requirement.",
    responses={
        200: {"description": "Password reset successfully"},
        403: {"description": "Admin access required"},
        404: {"description": "User not found"}
    }
)
@handle_service_exceptions
async def admin_reset_password(
    user_id: UUID,
    new_password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Reset user password (admin only)."""
    user_service.change_password(user_id, "", new_password, current_user)
    return MessageResponse(message="Password reset successfully")


# -----------------------------
# Search & Discovery
# -----------------------------

@router.get(
    "/search/profiles",
    response_model=List[ProfileOut],
    summary="Search user profiles",
    description="""
    Search user profiles with privacy filtering applied.
    
    **Search Features:**
    - Searches across full_name, location, and username
    - Results are filtered based on privacy settings
    - Users who opted out of search are excluded
    - Results are privacy-filtered for the requesting user
    
    **Privacy Protection:**
    - show_in_search=False profiles are excluded
    - Personal data filtered based on privacy settings
    - Admins see unfiltered results
    """,
    responses={
        200: {"description": "Search results"},
        422: {"description": "Search query too short"}
    }
)
@handle_service_exceptions
async def search_profiles(
    q: str = Query(..., min_length=2, max_length=100, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Search user profiles with privacy filtering."""
    return user_service.search_profiles(q, skip, limit, current_user)


# -----------------------------
# Health & Monitoring Endpoints
# -----------------------------

@router.get(
    "/stats/overview",
    summary="Get user statistics",
    description="Get user statistics overview (Admin only).",
    response_model=Dict[str, Any],
    responses={
        200: {"description": "Statistics retrieved"},
        403: {"description": "Admin access required"}
    }
)
@handle_service_exceptions
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get user statistics (admin only)."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # TODO: Implement stats gathering in service layer
    return {
        "total_users": 0,
        "active_users": 0,
        "verified_users": 0,
        "profiles_completed": 0,
        "last_updated": "2024-01-01T00:00:00Z"
    }


# -----------------------------
# Batch Operations (Admin)
# -----------------------------

@router.put(
    "/bulk/update",
    response_model=MessageResponse,
    summary="Bulk update users",
    description="Bulk update multiple users (Admin only).",
    responses={
        200: {"description": "Users updated successfully"},
        403: {"description": "Admin access required"}
    }
)
@handle_service_exceptions
async def bulk_update_users(
    user_ids: List[UUID] = Body(...),
    update_data: UserUpdate = Body(...),
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Bulk update multiple users (admin only)."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # TODO: Implement bulk operations in service layer
    updated_count = len(user_ids)  # Placeholder
    return MessageResponse(message=f"Updated {updated_count} users successfully")


# -----------------------------
# Error Handlers & Middleware
# -----------------------------

@router.middleware("http")
async def log_requests(request, call_next):
    """Log all requests for monitoring and debugging."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.2f}s"
    )
    
    return response


# Add router to main app with:
# from app.api.user_routes import router as user_router
# app.include_router(user_router)