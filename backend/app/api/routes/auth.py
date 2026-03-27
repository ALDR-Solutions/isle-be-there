from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import datetime
import secrets
import bcrypt
import logging

from app.core.email import send_verification_email
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    RegisterResponse,
    TokenResponse,
    RefreshTokenRequest,
    ResetPassword,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── helpers ──────────────────────────────────────────────────────────


def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.exec(select(User).where(User.email == email)).first()


def _get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.exec(select(User).where(User.id == user_id)).first()


# ── routes ───────────────────────────────────────────────────────────


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if _get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Create user
    hashed_pw = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_pw,
        is_verified=False,
        verification_token=verification_token,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    email_sent = True
    try:
        await send_verification_email(user.email, verification_token)
    except Exception:
        email_sent = False
        logger.exception(
            "Failed to send verification email for user_id=%s email=%s",
            user.id,
            user.email,
        )

    if email_sent:
        return {
            "message": "Registration successful. Please check your email to verify your account.",
            "email_sent": True,
        }

    return {
        "message": "Registration successful, but we could not send a verification email right now. Please try again later.",
        "email_sent": False,
    }

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.exec(
        select(User).where(User.verification_token == token)
    ).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user.is_verified = True
    user.verification_token = None  # invalidate after use
    db.add(user)
    db.commit()
    
    return {"message": "Email verified successfully. You can now log in."}


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = _get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    return {
        "access_token": create_access_token(data={"sub": str(user.id)}),
        "refresh_token": create_refresh_token(data={"sub": str(user.id)}),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(request.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = _get_user_by_id(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return {
        "access_token": create_access_token(data={"sub": str(user.id)}),
        "refresh_token": create_refresh_token(data={"sub": str(user.id)}),
        "token_type": "bearer",
    }


@router.post("/logout")
def logout():
    return {"detail": "logged out"}


@router.post("/reset-password")
def reset_password(
    data: ResetPassword,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = _get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(data.password)
    db.add(user)
    db.commit()
    return {"detail": "password updated"}


@router.get("/me", response_model=UserResponse)
def get_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = _get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.delete('/me', status_code=200)
def disable_account(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = _get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.add(user)
    db.commit()
    return {"detail": "Account disabled"}
