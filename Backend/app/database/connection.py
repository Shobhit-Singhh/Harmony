# app/database/connection.py
import os
import importlib
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Choose engine options depending on driver
if DATABASE_URL.startswith("sqlite"):
    # SQLite needs check_same_thread when used with multiple threads (FastAPI dev server)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # For postgres/mysql/etc.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy Session and closes it afterwards.
    Usage:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Import model modules so SQLAlchemy has all table metadata registered, then
    create tables on the configured engine.

    Call this during local development if you want to auto-create tables:
        from app.database.connection import create_tables
        create_tables()
    """
    # Import common model modules so their metadata is registered.
    # Add or remove module names to match your project structure.
    model_modules = [
        "app.models.user_models",
        "app.models.auth_models",
        "app.models.conversation_models",
        # add other model modules here as you create them
    ]
    for mod in model_modules:
        try:
            importlib.import_module(mod)
        except ModuleNotFoundError:
            # ignore if a module isn't present yet
            pass

    # Prefer a central Base if you have one (app/database/base.py). Fallback to user_models.Base.
    try:
        from app.database.base import Base  # if you created this file for Alembic
    except Exception:
        try:
            from app.models.user_models import Base
        except Exception:
            raise RuntimeError(
                "No SQLAlchemy Base found. Ensure either app/database/base.py defines Base "
                "or app/models/user_models.py defines Base."
            )

    Base.metadata.create_all(bind=engine)
