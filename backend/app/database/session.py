from typing import Generator
from sqlmodel import Session

from .engine import get_engine


def get_db() -> Generator:
    """Dependency for getting database session."""
    with Session(get_engine()) as db:
        yield db


__all__ = ["get_db"]
