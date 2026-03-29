from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.security import get_password_hash

from .models import User
from .schemas import ProfileUpdate, UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.exec(select(User).where(User.email == email)).first()


def get_user_by_id(db: Session, user_id: str | UUID) -> User | None:
    return db.exec(select(User).where(User.id == user_id)).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.exec(select(User).where(User.username == username)).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if user_data.username and get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_business=user_data.is_business,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_profile(db: Session, user_id: UUID, data: ProfileUpdate) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = data.model_dump(exclude_unset=True)

    username = updates.get("username")
    if username is not None:
        existing = get_user_by_username(db, username)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Username already taken")

    email = updates.get("email")
    if email is not None:
        existing = get_user_by_email(db, email)
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail="Email already registered")

    for key, value in updates.items():
        setattr(user, key, value)

    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_profile(db: Session, user_id: UUID) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def mark_interests_handled(db: Session, user_id: UUID) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.interests_handled = True
    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
