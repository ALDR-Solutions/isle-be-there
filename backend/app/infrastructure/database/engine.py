from functools import lru_cache

from sqlmodel import create_engine

from app.core.config import get_settings

from . import models


@lru_cache
def get_engine():
    settings = get_settings()
    return create_engine(
        settings.require_database_url(),
        echo=settings.SQL_ECHO,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_use_lifo=True,
    )
