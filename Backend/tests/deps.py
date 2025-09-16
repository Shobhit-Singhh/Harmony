# app/core/deps.py
"""
Core dependencies for FastAPI dependency injection.
This module provides reusable dependencies for database sessions,
authentication, and service layer injection.
"""

import time
import logging
from typing import Generator, Optional, Any
from uuid import UUID
from fastapi import Depends, HTTPException, status, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from Backend.tests.database import SessionLocal
from app.core.config import settings
from app.models.user_models import User, UserRole
from app.crud import user_crud
from app.services.user_service import UserService, get_user_service

logger = logging.getLogger(__name__)
security = HTTPBearer()


# -----------------------------
# Database Dependencies
# -----------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Creates a new database session for each request and closes it when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Authentication Dependencies
# -----------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: Bearer token from request header
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = user_crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    
    # Convert UserOut to User model (for compatibility)
    # This is a temporary solution - ideally we'd work with UserOut throughout
    user_dict = user.dict()
    user_obj = User(**user_dict)
    
    return user_obj


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (must be active and verified for sensitive operations).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current admin user (must be admin role).
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Current admin user
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_current_clinician_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current clinician user (must be clinician or admin role).
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Current clinician user
        
    Raises:
        HTTPException: If user is not clinician or admin
    """
    if current_user.role not in [UserRole.clinician, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinician access required"
        )
    return current_user


# -----------------------------
# Optional Authentication
# -----------------------------

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None if not.
    Useful for endpoints that work differently for authenticated vs anonymous users.
    
    Args:
        credentials: Optional bearer token
        db: Database session
        
    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None
        
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


# -----------------------------
# Service Dependencies
# -----------------------------

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    User service dependency.
    Creates a UserService instance with database session.
    """
    return UserService(db)


# -----------------------------
# Rate Limiting Dependencies
# -----------------------------

class RateLimiter:
    """Simple in-memory rate limiter for demonstration."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed under rate limit."""
        import time
        now = time.time()
        
        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items() 
            if now - v['first_request'] < self.window_seconds
        }
        
        # Check current key
        if key not in self.requests:
            self.requests[key] = {
                'count': 1,
                'first_request': now
            }
            return True
        
        # Check if limit exceeded
        if self.requests[key]['count'] >= self.max_requests:
            return False
        
        # Increment counter
        self.requests[key]['count'] += 1
        return True


# Global rate limiter instances
general_limiter = RateLimiter(max_requests=1000, window_seconds=3600)  # 1000/hour
auth_limiter = RateLimiter(max_requests=10, window_seconds=900)  # 10/15min for auth


def rate_limit_general(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> None:
    """
    General rate limiting based on IP or user ID.
    
    Args:
        request: FastAPI request object
        current_user: Optional current user
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    # Use user ID if authenticated, otherwise IP address
    key = str(current_user.id) if current_user else request.client.host
    
    if not general_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )


def rate_limit_auth(request: Request) -> None:
    """
    Stricter rate limiting for authentication endpoints.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    key = request.client.host
    
    if not auth_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Try again in 15 minutes."
        )


# -----------------------------
# Pagination Dependencies
# -----------------------------

class PaginationParams:
    """Pagination parameters for list endpoints."""
    
    def __init__(
        self,
        skip: int = Query(0, ge=0, le=10000, description="Number of items to skip"),
        limit: int = Query(20, ge=1, le=100, description="Number of items to return")
    ):
        self.skip = skip
        self.limit = limit


def get_pagination_params(
    skip: int = Query(0, ge=0, le=10000, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return")
) -> PaginationParams:
    """Get pagination parameters with validation."""
    return PaginationParams(skip=skip, limit=limit)


# -----------------------------
# Search Dependencies
# -----------------------------

class SearchParams:
    """Search parameters for search endpoints."""
    
    def __init__(
        self,
        q: str = Query(..., min_length=2, max_length=100, description="Search query"),
        skip: int = Query(0, ge=0, description="Number of results to skip"),
        limit: int = Query(20, ge=1, le=100, description="Number of results to return")
    ):
        self.query = q.strip()
        self.skip = skip
        self.limit = limit


def get_search_params(
    q: str = Query(..., min_length=2, max_length=100, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return")
) -> SearchParams:
    """Get search parameters with validation."""
    return SearchParams(q=q, skip=skip, limit=limit)


# -----------------------------
# Permission Dependencies
# -----------------------------

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role for endpoint access."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_clinician_or_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require clinician or admin role for endpoint access."""
    if current_user.role not in [UserRole.clinician, UserRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinician or admin privileges required"
        )
    return current_user


def require_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Require verified user for sensitive operations."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required for this operation"
        )
    return current_user


# -----------------------------
# Resource Access Dependencies
# -----------------------------

def get_user_or_404(
    user_id: UUID,
    db: Session = Depends(get_db)
) -> User:
    """
    Get user by ID or raise 404.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User: User object
        
    Raises:
        HTTPException: If user not found
    """
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Convert UserOut to User model
    user_dict = user.dict()
    return User(**user_dict)


def require_user_access(
    target_user_id: UUID,
    current_user: User = Depends(get_current_active_user)
) -> UUID:
    """
    Require that current user can access target user's data.
    Users can access their own data, admins can access any user's data.
    
    Args:
        target_user_id: ID of user being accessed
        current_user: Current authenticated user
        
    Returns:
        UUID: Target user ID if access allowed
        
    Raises:
        HTTPException: If access denied
    """
    if current_user.id != target_user_id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: can only access own data or admin required"
        )
    return target_user_id


# -----------------------------
# Validation Dependencies
# -----------------------------

def validate_uuid(
    uuid_str: str,
    field_name: str = "ID"
) -> UUID:
    """
    Validate UUID string and convert to UUID object.
    
    Args:
        uuid_str: UUID string
        field_name: Name of field for error message
        
    Returns:
        UUID: Valid UUID object
        
    Raises:
        HTTPException: If UUID is invalid
    """
    try:
        return UUID(uuid_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {field_name} format"
        )


# -----------------------------
# Monitoring Dependencies
# -----------------------------

def get_request_context(request: Request) -> dict:
    """
    Get request context for logging and monitoring.
    
    Args:
        request: FastAPI request object
        
    Returns:
        dict: Request context information
    """
    return {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "timestamp": time.time()
    }


# -----------------------------
# Cache Dependencies (Future)
# -----------------------------

class CacheService:
    """Simple cache service for demonstration (use Redis in production)."""
    
    def __init__(self):
        self._cache = {}
        self._ttl = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            # Check TTL
            if time.time() > self._ttl.get(key, float('inf')):
                del self._cache[key]
                if key in self._ttl:
                    del self._ttl[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Set value in cache with TTL."""
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl_seconds
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]


# Global cache instance
cache_service = CacheService()


def get_cache_service() -> CacheService:
    """Get cache service dependency."""
    return cache_service


# -----------------------------
# Health Check Dependencies
# -----------------------------

def check_database_health(db: Session = Depends(get_db)) -> bool:
    """
    Check database connectivity.
    
    Args:
        db: Database session
        
    Returns:
        bool: True if database is healthy
    """
    try:
        # Simple query to check database connectivity
        db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


def check_service_health(
    db_healthy: bool = Depends(check_database_health)
) -> dict:
    """
    Overall service health check.
    
    Args:
        db_healthy: Database health status
        
    Returns:
        dict: Service health status
    """
    return {
        "database": "healthy" if db_healthy else "unhealthy",
        "cache": "healthy",  # Placeholder
        "timestamp": time.time()
    }


# Example usage in main.py:
"""
from app.core.deps import (
    get_db, get_current_user, get_current_active_user,
    get_current_admin_user, rate_limit_general, rate_limit_auth
)

# Apply rate limiting to all routes
app.middleware("http")(rate_limit_general)

# Or apply to specific endpoints:
@app.post("/auth/login", dependencies=[Depends(rate_limit_auth)])
async def login(...):
    pass
"""