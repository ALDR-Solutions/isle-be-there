from datetime import datetime, timezone
import logging
import secrets

from fastapi import HTTPException, BackgroundTasks
from sqlmodel import Session, select

from app.core.email import send_verification_email, send_password_reset_email
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    decode_reset_password_token,
    get_password_hash,
    verify_password,
    create_reset_password_token,
)
from app.modules.users.models import User
from app.modules.users.schemas import (
    PasswordResetConfirm,
    RefreshTokenRequest,
    ResetPassword,
    ResetRequest,
    UserCreate,
)
from app.modules.users.service import create_user, get_user_by_email, get_user_by_id


logger = logging.getLogger(__name__)


def register_user(db: Session, user_data: UserCreate) -> User:
    return create_user(db, user_data)


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
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
    user.updated_at = datetime.utcnow()
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

def verify_email(token: str, db: Session):
    user = db.exec(select(User).where(User.verification_token == token)).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")

    user.is_verified = True
    user.verification_token = None
    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()


def resend_verification_email_for_user(db: Session, email: str) -> None:
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email is already verified")

    user.verification_token = secrets.token_urlsafe(32)
    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        send_verification_email(user.email, user.verification_token)
    except Exception:
        logger.exception("Failed to resend verification email for user %s", user.email)
        raise HTTPException(status_code=502, detail="Failed to send verification email")

def forget_password(db: Session, data: ResetRequest, background_tasks: BackgroundTasks) -> None:
    user = get_user_by_email(db, data.email)
    if not user:
        logger.info("Password reset requested for unknown email: %s", data.email)
        return

    secret_token = create_reset_password_token(email=user.email)
    background_tasks.add_task(send_password_reset_email, user.email, secret_token)

    logger.info("Password reset requested for email: %s", data.email)


def reset_password_with_token(db: Session, data: PasswordResetConfirm) -> None:
    email = decode_reset_password_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(data.password)
    user.updated_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
