# config.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic_settings import BaseSettings

# ---------------------------
# 1. Settings
# ---------------------------
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    REFRESH_SECRET_KEY: str = "Harmonysecretkey"
    SECRET_KEY: str = "Supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3

settings = Settings()

# ---------------------------
# 2. Database Engine & Session
# ---------------------------
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------
# 3. Base Model
# ---------------------------
Base = declarative_base()

# ---------------------------
# 4. Dependency for FastAPI
# ---------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
