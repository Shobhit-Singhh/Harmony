# app/core/security.py

from passlib.context import CryptContext

# Create a password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password (str): The plaintext password
    
    Returns:
        str: A bcrypt hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the stored hashed password.
    
    Args:
        plain_password (str): The raw password input
        hashed_password (str): The stored bcrypt hash
    
    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)
