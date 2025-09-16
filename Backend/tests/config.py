# app/core/config.py
"""
Application configuration management.
This module handles all configuration settings for the application,
including database, security, and feature flags.
"""

import os
from typing import Any, Dict, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application
    APP_NAME: str = "Mental Health Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/mental_health_db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 50
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password requirements
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_PASSWORD_UPPERCASE: bool = True
    REQUIRE_PASSWORD_LOWERCASE: bool = True
    REQUIRE_PASSWORD_NUMBERS: bool = True
    REQUIRE_PASSWORD_SPECIAL: bool = True
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_GENERAL: int = 1000  # requests per hour
    RATE_LIMIT_AUTH: int = 10       # auth attempts per 15 minutes
    
    # Caching
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300
    REDIS_URL: Optional[str] = None
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48
    
    # File Storage
    UPLOAD_FOLDER: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"}
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    
    # Features
    ENABLE_REGISTRATION: bool = True
    ENABLE_EMAIL_VERIFICATION: bool = True
    ENABLE_PASSWORD_RESET: bool = True
    ENABLE_PROFILE_SEARCH: bool = True
    ENABLE_ANALYTICS: bool = False
    
    # Mental Health Specific
    CRISIS_HOTLINE: str = "988"  # US Suicide & Crisis Lifeline
    MIN_AGE_REQUIREMENT: int = 13
    MAX_AGE_ALLOWED: int = 120
    
    # Wellness Features
    ENABLE_MOOD_TRACKING: bool = True
    ENABLE_GOAL_SETTING: bool = True
    ENABLE_PEER_SUPPORT: bool = True
    ENABLE_CLINICIAN_NOTES: bool = True
    
    # Privacy & Compliance
    DATA_RETENTION_DAYS: int = 2555  # ~7 years for healthcare
    GDPR_COMPLIANCE: bool = True
    HIPAA_COMPLIANCE: bool = False
    REQUIRE_PRIVACY_ACCEPTANCE: bool = True
    
    # External Services
    OPENAI_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        """Assemble database URL from components if needed."""
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v
        
        # If individual components are provided, assemble them
        db_user = os.getenv("DB_USER", "user")
        db_password = os.getenv("DB_PASSWORD", "password")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "mental_health_db")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list) -> list:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key strength."""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        if v == "your-secret-key-change-in-production":
            import warnings
            warnings.warn("Using default SECRET_KEY - change this in production!")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
    
    @property
    def database_url_async(self) -> str:
        """Get asynchronous database URL."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


class DevelopmentSettings(Settings):
    """Development-specific settings."""
    DEBUG: bool = True
    RELOAD: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]


class ProductionSettings(Settings):
    """Production-specific settings."""
    DEBUG: bool = False
    RELOAD: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"
    RATE_LIMIT_ENABLED: bool = True
    CACHE_ENABLED: bool = True
    ENABLE_ANALYTICS: bool = True


class TestingSettings(Settings):
    """Testing-specific settings."""
    DATABASE_URL: str = "postgresql://test_user:test_password@localhost/test_mental_health_db"
    SECRET_KEY: str = "test-secret-key-for-testing-only-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    RATE_LIMIT_ENABLED: bool = False
    CACHE_ENABLED: bool = False
    ENABLE_EMAIL_VERIFICATION: bool = False


def get_settings() -> Settings:
    """
    Get application settings based on environment.
    
    Returns:
        Settings: Configuration object
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()


# Logging configuration
def setup_logging():
    """Setup logging configuration based on settings."""
    import logging.config
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": settings.LOG_FORMAT
            },
        },
        "handlers": {
            "default": {
                "level": settings.LOG_LEVEL,
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default"],
                "level": settings.LOG_LEVEL,
                "propagate": False
            },
            "uvicorn.error": {
                "level": settings.LOG_LEVEL,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
        }
    }
    
    # Add file handler if log file specified
    if settings.LOG_FILE:
        logging_config["handlers"]["file"] = {
            "level": settings.LOG_LEVEL,
            "formatter": "standard", 
            "class": "logging.FileHandler",
            "filename": settings.LOG_FILE,
        }
        logging_config["loggers"][""]["handlers"].append("file")
    
    logging.config.dictConfig(logging_config)


# Initialize logging on import
setup_logging()


# Export commonly used settings
__all__ = [
    "settings",
    "Settings", 
    "DevelopmentSettings",
    "ProductionSettings", 
    "TestingSettings",
    "get_settings",
    "setup_logging"
]