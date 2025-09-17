# app/crud/user_crud.py
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models.user_models import User, UserProfile, UserRole
from v1.user_schema import (
    UserCreate,
    UserUpdate,
    UserOut,
    ProfileCreate,
    ProfileUpdate, 
    ProfileOut,
)

# -----------------------------
# User CRUD Operations
# -----------------------------

def get_user_by_id(db: Session, user_id: UUID) -> Optional[UserOut]:
    """
    Retrieve a user by their UUID.
    
    Args:
        db (Session): SQLAlchemy DB session
        user_id (UUID): UUID of the user to retrieve
        
    Returns:
        Optional[UserOut]: User data if found, else None
    """
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        return None
    return UserOut.from_orm(user)


def get_user_by_email(db: Session, email: str) -> Optional[UserOut]:
    """
    Retrieve a user by their email address.
    
    Args:
        db (Session): SQLAlchemy DB session
        email (str): Email of the user to retrieve
        
    Returns:
        Optional[UserOut]: User data if found, else None
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    return UserOut.from_orm(user)


def get_user_by_phone(db: Session, phone_number: str) -> Optional[UserOut]:
    """
    Retrieve a user by their phone number.
    
    Args:
        db (Session): SQLAlchemy DB session
        phone_number (str): Phone number of the user to retrieve
        
    Returns:
        Optional[UserOut]: User data if found, else None
    """
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if not user:
        return None
    return UserOut.from_orm(user)


def get_user_by_username(db: Session, username: str) -> Optional[UserOut]:
    """
    Retrieve a user by their username.
    
    Args:
        db (Session): SQLAlchemy DB session
        username (str): Username of the user to retrieve
        
    Returns:
        Optional[UserOut]: User data if found, else None
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    return UserOut.from_orm(user)


def create_user(db: Session, user_in: UserCreate, password_hash: str) -> UserOut:
    """
    Create a new user record.

    Args:
        db (Session): SQLAlchemy DB session
        user_in (UserCreate): User creation data
        password_hash (str): Hashed password

    Returns:
        UserOut: Created user data

    Raises:
        IntegrityError: If duplicate email/username/phone
    """
    db_user = User(
        email=user_in.email,
        phone_number=user_in.phone_number,
        username=user_in.username,
        password_hash=password_hash,
        is_active=True,
        is_verified=False,
        role=getattr(user_in, 'role', UserRole.user)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserOut.from_orm(db_user)


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> UserOut:
    """
    Update user fields (excluding password and immutable fields).

    Args:
        db (Session): SQLAlchemy DB session
        db_user (User): Existing user ORM instance
        user_update (UserUpdate): Update data

    Returns:
        UserOut: Updated user data
    """
    update_data = user_update.dict(exclude_unset=True, exclude={'password'})
    
    for field, value in update_data.items():
        if hasattr(db_user, field): 
            setattr(db_user, field, value)
    
    db_user.updated_at = datetime.now(timezone.utc)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserOut.from_orm(db_user)


def update_user_password(db: Session, db_user: User, password_hash: str) -> None:
    """
    Update user password hash.

    Args:
        db (Session): SQLAlchemy DB session
        db_user (User): Existing user ORM instance
        password_hash (str): New hashed password
    """
    db_user.password_hash = password_hash
    db_user.updated_at = datetime.now(timezone.utc)

    db.add(db_user)
    db.commit()


def update_last_login(db: Session, user_id: UUID) -> None:
    """
    Update user's last login timestamp.

    Args:
        db (Session): SQLAlchemy DB session
        user_id (UUID): User ID
    """
    db.query(User).filter(User.id == user_id).update({
        'last_login_at': datetime.now(timezone.utc)
    })
    db.commit()


def list_users(db: Session, skip: int = 0, limit: int = 100, 
               filters: Optional[Dict[str, Any]] = None) -> List[UserOut]:
    """
    List users with pagination and optional filtering.

    Args:
        db (Session): SQLAlchemy DB session
        skip (int): Offset for pagination
        limit (int): Limit for pagination
        filters (Optional[Dict]): Optional filters (role, is_active, etc.)

    Returns:
        List[UserOut]: List of user data
    """
    query = db.query(User).order_by(User.created_at.desc())
    
    # Apply filters
    if filters:
        if 'role' in filters:
            query = query.filter(User.role == filters['role'])
        if 'is_active' in filters:
            query = query.filter(User.is_active == filters['is_active'])
        if 'is_verified' in filters:
            query = query.filter(User.is_verified == filters['is_verified'])
        if 'email_domain' in filters:
            query = query.filter(User.email.like(f"%@{filters['email_domain']}"))
    
    users = query.offset(skip).limit(limit).all()
    return [UserOut.from_orm(user) for user in users]


def activate_user(db: Session, db_user: User) -> UserOut:
    """
    Activate a user account.

    Args:
        db (Session): SQLAlchemy DB session
        db_user (User): User ORM instance

    Returns:
        UserOut: Updated user data
    """
    db_user.is_active = True
    db_user.updated_at = datetime.now(timezone.utc)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserOut.from_orm(db_user)


def deactivate_user(db: Session, db_user: User) -> UserOut:
    """
    Soft delete (deactivate) user account.

    Args:
        db (Session): SQLAlchemy DB session
        db_user (User): User ORM instance

    Returns:
        UserOut: Updated user data
    """
    db_user.is_active = False 
    db_user.updated_at = datetime.now(timezone.utc)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserOut.from_orm(db_user)


def delete_user(db: Session, db_user: User, hard_delete: bool = False) -> bool:
    """
    Delete user record (hard delete removes from DB).

    Args:
        db (Session): SQLAlchemy DB session
        db_user (User): User ORM instance
        hard_delete (bool): If True, permanently delete; if False, soft delete

    Returns:
        bool: True if deleted, False if user not found
    """
    if not db_user:
        return False
        
    if hard_delete:
        # Hard delete: remove from database
        db.delete(db_user)
    else:
        # Soft delete: deactivate user
        db_user.is_active = False
        db_user.updated_at = datetime.now(timezone.utc)
        db.add(db_user)
    
    db.commit()
    return True


# -----------------------------
# UserProfile CRUD Operations
# -----------------------------

def get_profile_by_user_id(db: Session, user_id: UUID) -> Optional[ProfileOut]:
    """
    Retrieve user profile by user ID.

    Args:
        db (Session): SQLAlchemy DB session
        user_id (UUID): User ID

    Returns:
        Optional[ProfileOut]: Profile data if found, else None
    """
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not profile:
        return None
    return ProfileOut.from_orm(profile)


def create_profile(db: Session, user_id: UUID, profile_create: ProfileCreate) -> ProfileOut:
    """
    Create user profile.

    Args:
        db (Session): SQLAlchemy DB session
        user_id (UUID): User ID
        profile_create (ProfileCreate): Profile creation data

    Returns:
        ProfileOut: Created profile data

    Raises:
        IntegrityError: If profile already exists or user doesn't exist
    """
    db_profile = UserProfile(
        id=user_id,
        full_name=profile_create.full_name,
        date_of_birth=profile_create.date_of_birth,
        gender=profile_create.gender,
        location=profile_create.location,
        timezone=profile_create.timezone,
        primary_pillar_weights=(
            profile_create.primary_pillar_weights 
            if profile_create.primary_pillar_weights else None
        ),
        medications=profile_create.medications,
        conditions=profile_create.conditions,
        crisis_contact=profile_create.crisis_contact,
        preferred_language=profile_create.preferred_language,
        privacy_settings=profile_create.privacy_settings,
        onboarding_completed=profile_create.onboarding_completed or False,
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return ProfileOut.from_orm(db_profile)


def update_profile(db: Session, db_profile: UserProfile, profile_update: ProfileUpdate) -> ProfileOut:
    """
    Update user profile.

    Args:
        db (Session): SQLAlchemy DB session
        db_profile (UserProfile): Existing profile ORM instance
        profile_update (ProfileUpdate): Profile update data

    Returns:
        ProfileOut: Updated profile data
    """
    update_data = profile_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(db_profile, field):
            setattr(db_profile, field, value)
    
    db_profile.last_updated_at = datetime.now(timezone.utc)
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return ProfileOut.from_orm(db_profile)


def delete_profile(db: Session, db_profile: UserProfile) -> bool:
    """
    Delete user profile.

    Args:
        db (Session): SQLAlchemy DB session
        db_profile (UserProfile): Profile ORM instance to delete

    Returns:
        bool: True if deleted, False if profile not found
    """
    if not db_profile:
        return False
    
    db.delete(db_profile)
    db.commit()
    return True


def search_profiles(db: Session, query: str, skip: int = 0, limit: int = 20) -> List[ProfileOut]:
    """
    Search user profiles by name, location, or other searchable fields.

    Args:
        db (Session): SQLAlchemy DB session
        query (str): Search query
        skip (int): Offset for pagination
        limit (int): Limit for pagination

    Returns:
        List[ProfileOut]: List of matching profiles
    """
    # Join with User table to ensure we only get active users
    search_query = db.query(UserProfile).join(User).filter(
        User.is_active == True,
        or_(
            UserProfile.full_name.ilike(f"%{query}%"),
            UserProfile.location.ilike(f"%{query}%"),
            User.username.ilike(f"%{query}%")
        )
    ).order_by(UserProfile.last_updated_at.desc())
    
    profiles = search_query.offset(skip).limit(limit).all()
    return [ProfileOut.from_orm(profile) for profile in profiles]


def get_profiles_by_conditions(db: Session, conditions: List[str], skip: int = 0, limit: int = 20) -> List[ProfileOut]:
    """
    Find profiles by health conditions (for matching/support groups).

    Args:
        db (Session): SQLAlchemy DB session
        conditions (List[str]): List of conditions to match
        skip (int): Offset for pagination
        limit (int): Limit for pagination

    Returns:
        List[ProfileOut]: List of matching profiles
    """
    # Join with User table to ensure we only get active users
    query = db.query(UserProfile).join(User).filter(
        User.is_active == True,
        UserProfile.conditions.op('&&')(conditions)  # PostgreSQL array overlap operator
    ).order_by(UserProfile.last_updated_at.desc())
    
    profiles = query.offset(skip).limit(limit).all()
    return [ProfileOut.from_orm(profile) for profile in profiles]


def get_user_count(db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
    """
    Get total count of users with optional filtering.

    Args:
        db (Session): SQLAlchemy DB session
        filters (Optional[Dict]): Optional filters

    Returns:
        int: Total count of users
    """
    query = db.query(func.count(User.id))
    
    # Apply same filters as list_users
    if filters:
        if 'role' in filters:
            query = query.filter(User.role == filters['role'])
        if 'is_active' in filters:
            query = query.filter(User.is_active == filters['is_active'])
        if 'is_verified' in filters:
            query = query.filter(User.is_verified == filters['is_verified'])
        if 'email_domain' in filters:
            query = query.filter(User.email.like(f"%@{filters['email_domain']}"))
    
    return query.scalar()


def get_profile_count(db: Session) -> int:
    """
    Get total count of profiles.

    Args:
        db (Session): SQLAlchemy DB session

    Returns:
        int: Total count of profiles
    """
    return db.query(func.count(UserProfile.id)).scalar()


def bulk_update_users(db: Session, user_ids: List[UUID], 
                     update_data: Dict[str, Any]) -> int:
    """
    Bulk update multiple users (admin operation).

    Args:
        db (Session): SQLAlchemy DB session
        user_ids (List[UUID]): List of user IDs to update
        update_data (Dict): Fields to update

    Returns:
        int: Number of users updated
    """
    # Add timestamp
    update_data['updated_at'] = datetime.now(timezone.utc)
    
    result = db.query(User).filter(User.id.in_(user_ids)).update(
        update_data, synchronize_session=False
    )
    db.commit()
    return result


def get_users_by_role(db: Session, role: str, skip: int = 0, limit: int = 100) -> List[UserOut]:
    """
    Get users by role.

    Args:
        db (Session): SQLAlchemy DB session
        role (str): User role to filter by
        skip (int): Offset for pagination
        limit (int): Limit for pagination

    Returns:
        List[UserOut]: List of users with the specified role
    """
    users = db.query(User).filter(
        User.role == role,
        User.is_active == True
    ).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return [UserOut.from_orm(user) for user in users]


def get_recently_active_users(db: Session, days: int = 30, 
                             skip: int = 0, limit: int = 100) -> List[UserOut]:
    """
    Get users who were active within the specified number of days.

    Args:
        db (Session): SQLAlchemy DB session
        days (int): Number of days to look back
        skip (int): Offset for pagination
        limit (int): Limit for pagination

    Returns:
        List[UserOut]: List of recently active users
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    users = db.query(User).filter(
        User.last_login_at >= cutoff_date,
        User.is_active == True
    ).order_by(User.last_login_at.desc()).offset(skip).limit(limit).all()
    
    return [UserOut.from_orm(user) for user in users]


def verify_user_email(db: Session, user_id: UUID) -> UserOut:
    """
    Mark user email as verified.

    Args:
        db (Session): SQLAlchemy DB session
        user_id (UUID): User ID

    Returns:
        UserOut: Updated user data
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
        
    user.is_verified = True
    user.updated_at = datetime.now(timezone.utc)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserOut.from_orm(user)