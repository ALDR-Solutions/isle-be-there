from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlmodel import create_engine

ROOT_DIR = Path(__file__).resolve().parents[4]
ENV_FILES = (str(ROOT_DIR / ".env"), str(ROOT_DIR / "backend" / ".env"))


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str
    SQL_ECHO: bool = False

    model_config = SettingsConfigDict(env_file=ENV_FILES, extra="ignore")


@lru_cache
def get_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache
def get_engine():
    settings = get_settings()
    return create_engine(
        settings.DATABASE_URL,
        echo=settings.SQL_ECHO,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
