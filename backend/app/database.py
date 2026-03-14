"""
Database configuration and session management.

Note: This module provides SQLAlchemy setup for import compatibility.
The actual database operations use Supabase client directly.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os

# Database URL - not used since we're using Supabase directly
# but required for SQLAlchemy setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/islebethere")

# Create SQLAlchemy engine (lazy - only connects when actually used)
# For now, we don't actually connect since Supabase is used directly
engine = None


def get_engine():
    """Lazy engine creation - only when needed."""
    global engine
    if engine is None:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
    return engine


# Create SessionLocal class for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=None)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency for getting database session.
    
    Note: This provides SQLAlchemy sessions, but the API endpoints
    use Supabase client directly for database operations.
    This is kept for potential future use and to satisfy imports.
    """
    # Get or create engine lazily
    try:
        engine = get_engine()
        SessionLocal.configure(bind=engine)
    except Exception:
        # If we can't connect, still yield a session
        # This allows imports to work even without DB
        pass
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Re-export for convenience
__all__ = ["engine", "SessionLocal", "Base", "get_db", "get_engine"]
