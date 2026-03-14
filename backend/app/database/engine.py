"""
Database engine configuration (lazy initialization).

Note: This module provides the SQLAlchemy engine for Postgres access.
"""
from pathlib import Path
from sqlmodel import create_engine
from pydantic_settings import BaseSettings


ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILES = (str(ROOT_DIR / ".env"), str(ROOT_DIR / "backend" / ".env"))


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str
    model_config = {"env_file": ENV_FILES, "extra": "ignore"}


settings = DatabaseSettings()
DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine (lazy - only connects when actually used)
engine = None


def get_engine():
    """Lazy engine creation - only when needed."""
    global engine
    if engine is None:
        engine = create_engine(
            DATABASE_URL,
            echo=True,  # Enable SQL query logging for debugging
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    return engine

__all__ = ["engine", "get_engine", "DATABASE_URL", "settings"]
