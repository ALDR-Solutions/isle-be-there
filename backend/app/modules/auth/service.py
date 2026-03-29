from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.modules.users.models import User
from app.modules.users.schemas import RefreshTokenRequest, ResetPassword, UserCreate
from app.modules.users.service import create_user, get_user_by_email, get_user_by_id


def register_user(db: Session, user_data: UserCreate) -> User:
    return create_user(db, user_data)


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    return user


def build_token_response(user: User) -> dict:
    return {
        "access_token": create_access_token(data={"sub": str(user.id)}),
        "refresh_token": create_refresh_token(data={"sub": str(user.id)}),
        "token_type": "bearer",
    }


def refresh_user_token(db: Session, request: RefreshTokenRequest) -> dict:
    payload = decode_token(request.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = get_user_by_id(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return build_token_response(user)


def reset_authenticated_user_password(db: Session, user_id: str, data: ResetPassword) -> None:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(data.password)
    db.add(user)
    db.commit()


def disable_user_account(db: Session, user_id: str) -> None:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
