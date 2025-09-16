# app/core/database.py
"""
Database configuration and session management.
This module handles SQLAlchemy database setup, connection pooling, and session management for the application.
"""

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database engine configuration
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_size": settings.DATABASE_POOL_SIZE,
    "max_overflow": settings.DATABASE_MAX_OVERFLOW,
    "echo": settings.DATABASE_ECHO,
}

# Handle SQLite for testing (if needed)
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    })
    # Remove PostgreSQL-specific options for SQLite
    engine_kwargs.pop("pool_size", None)
    engine_kwargs.pop("max_overflow", None)

# Create database engine
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


# Database event listeners for monitoring and optimization
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance (if using SQLite)."""
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries for performance monitoring."""
    context._query_start_time = time.time()


@event.listens_for(Engine, "after_cursor_execute") 
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries for performance monitoring."""
    total = time.time() - context._query_start_time
    if total > 0.5:  # Log queries taking more than 500ms
        logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}...")


# Database utilities
def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop all database tables (use with caution)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def get_db_session() -> Session:
    """
    Get a database session.
    
    Returns:
        Session: SQLAlchemy database session
    """
    return SessionLocal()


def check_db_connection() -> bool:
    """
    Check database connectivity.
    
    Returns:
        bool: True if database is accessible, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


class DatabaseManager:
    """Database management utility class."""
    
    @staticmethod
    def get_session() -> Session:
        """Get a new database session."""
        return SessionLocal()
    
    @staticmethod
    def health_check() -> dict:
        """
        Perform database health check.
        
        Returns:
            dict: Health check results
        """
        try:
            start_time = time.time()
            with engine.connect() as connection:
                result = connection.execute("SELECT 1").fetchone()
                response_time = time.time() - start_time
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time * 1000, 2),
                    "database_url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "hidden",
                    "pool_size": engine.pool.size(),
                    "checked_out_connections": engine.pool.checkedout(),
                }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "response_time_ms": None
            }
    
    @staticmethod
    def get_stats() -> dict:
        """
        Get database statistics.
        
        Returns:
            dict: Database statistics
        """
        try:
            with engine.connect() as connection:
                # Get basic stats (PostgreSQL specific)
                if "postgresql" in settings.DATABASE_URL:
                    stats_query = """
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_tuples,
                        n_dead_tup as dead_tuples
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                    LIMIT 10;
                    """
                    result = connection.execute(stats_query).fetchall()
                    
                    return {
                        "table_stats": [dict(row) for row in result],
                        "pool_size": engine.pool.size(),
                        "checked_out_connections": engine.pool.checkedout(),
                        "overflow_connections": engine.pool.overflow(),
                    }
                else:
                    return {
                        "message": "Detailed stats only available for PostgreSQL",
                        "pool_size": engine.pool.size(),
                        "checked_out_connections": engine.pool.checkedout(),
                    }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}


# Transaction context managers
class DatabaseTransaction:
    """Context manager for database transactions."""
    
    def __init__(self, session: Session = None):
        self.session = session or SessionLocal()
        self.should_close = session is None
    
    def __enter__(self) -> Session:
        """Enter transaction context."""
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        if exc_type:
            self.session.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            try:
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                logger.error(f"Transaction commit failed: {e}")
                raise
            
            finally:
                if self.should_close:
                    self.session.close()


# Async database support (for future use)
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.ext.asyncio import sessionmaker as async_sessionmaker
    
    # Create async engine
    async_engine = create_async_engine(
        settings.database_url_async,
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
    )
    
    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async def get_async_db_session():
        """Get async database session."""
        async with AsyncSessionLocal() as session:
            yield session
    
    ASYNC_SUPPORT = True
    logger.info("Async database support enabled")
    
except ImportError:
    ASYNC_SUPPORT = False
    logger.info("Async database support not available")
    async_engine = None
    AsyncSessionLocal = None
    get_async_db_session = None


# Database initialization
def init_db():
    """
    Initialize database with tables and basic data.
    This function should be called on application startup.
    """
    try:
        logger.info("Initializing database...")
        
        # Check connection first
        if not check_db_connection():
            raise Exception("Cannot connect to database")
        
        # Create tables
        create_tables()
        
        # Insert initial data if needed
        with DatabaseTransaction() as db:
            # Check if we need to create initial admin user
            from app.crud import user_crud
            from v1.user_schema import UserCreate
            from app.core.security import hash_password
            
            admin_email = "admin@example.com"
            existing_admin = user_crud.get_user_by_email(db, admin_email)
            
            if not existing_admin:
                logger.info("Creating initial admin user...")
                admin_user = UserCreate(
                    username="admin",
                    email=admin_email,
                    password="AdminPass123!",
                    phone_number=None
                )
                hashed_password = hash_password("AdminPass123!")
                user_crud.create_user(db, admin_user, hashed_password)
                logger.info("Initial admin user created")
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Backup and maintenance utilities
def backup_database(backup_path: str = None):
    """
    Create database backup (PostgreSQL only).
    
    Args:
        backup_path: Path for backup file
    """
    if not "postgresql" in settings.DATABASE_URL:
        raise NotImplementedError("Backup only supported for PostgreSQL")
    
    import subprocess
    import os
    from datetime import datetime
    
    if not backup_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backup_{timestamp}.sql"
    
    try:
        # Parse database URL for pg_dump
        db_url = settings.DATABASE_URL
        # Extract components for pg_dump command
        # This is simplified - in production, use proper URL parsing
        
        cmd = [
            "pg_dump",
            db_url,
            "-f", backup_path,
            "--verbose"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {e.stderr}")
        raise
    except FileNotFoundError:
        logger.error("pg_dump not found. Install PostgreSQL client tools.")
        raise


def vacuum_database():
    """
    Perform database maintenance (PostgreSQL only).
    """
    if not "postgresql" in settings.DATABASE_URL:
        logger.info("Vacuum only supported for PostgreSQL")
        return
    
    try:
        with engine.connect() as connection:
            # Note: VACUUM cannot be run inside a transaction
            connection.execute("VACUUM ANALYZE;")
        logger.info("Database vacuum completed")
    except Exception as e:
        logger.error(f"Database vacuum failed: {e}")
        raise


# Export utilities
__all__ = [
    "engine",
    "SessionLocal", 
    "Base",
    "create_tables",
    "drop_tables",
    "get_db_session",
    "check_db_connection",
    "DatabaseManager",
    "DatabaseTransaction",
    "init_db",
    "backup_database",
    "vacuum_database",
    "ASYNC_SUPPORT",
]

# Add async exports if available
if ASYNC_SUPPORT:
    __all__.extend([
        "async_engine",
        "AsyncSessionLocal",
        "get_async_db_session",
    ])


# Application startup database check
def startup_database_check():
    """
    Perform startup database checks.
    This should be called when the application starts.
    """
    logger.info("Performing startup database checks...")
    
    try:
        # Check basic connectivity
        if not check_db_connection():
            raise Exception("Database connection failed")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.info("No tables found, initializing database...")
            init_db()
        else:
            logger.info(f"Database ready with {len(tables)} tables")
        
        # Print health status
        health = DatabaseManager.health_check()
        logger.info(f"Database health: {health['status']} "
                   f"(response: {health.get('response_time_ms', 'N/A')}ms)")
        
    except Exception as e:
        logger.error(f"Startup database check failed: {e}")
        raise


# Optional: Database migration support placeholder
class MigrationManager:
    """
    Simple migration manager placeholder.
    In production, use Alembic for proper migrations.
    """
    
    @staticmethod
    def get_current_version() -> str:
        """Get current database schema version."""
        try:
            with engine.connect() as connection:
                result = connection.execute(
                    "SELECT version FROM schema_version ORDER BY id DESC LIMIT 1"
                ).fetchone()
                return result[0] if result else "0"
        except:
            return "0"  # No version table exists
    
    @staticmethod
    def create_version_table():
        """Create schema version tracking table."""
        try:
            with engine.connect() as connection:
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(50) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    )
                """)
                connection.commit()
        except Exception as e:
            logger.error(f"Failed to create version table: {e}")
    
    @staticmethod
    def record_migration(version: str, description: str = None):
        """Record a completed migration."""
        try:
            with engine.connect() as connection:
                connection.execute(
                    "INSERT INTO schema_version (version, description) VALUES (%s, %s)",
                    (version, description)
                )
                connection.commit()
                logger.info(f"Migration {version} recorded")
        except Exception as e:
            logger.error(f"Failed to record migration: {e}")


# Example usage:
"""
# In main.py or app startup:
from app.core.database import startup_database_check, DatabaseManager

@app.on_event("startup")
async def startup():
    startup_database_check()
    
    # Optional: Print database stats
    stats = DatabaseManager.get_stats()
    print(f"Database stats: {stats}")

@app.on_event("shutdown") 
async def shutdown():
    # Close database connections
    engine.dispose()
    if ASYNC_SUPPORT and async_engine:
        await async_engine.dispose()
"""