from functools import lru_cache

from sqlmodel import create_engine

from app.core.config import get_settings


@lru_cache
def get_engine():
    settings = get_settings()
    return create_engine(
        settings.require_database_url(),
        echo=settings.SQL_ECHO,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
