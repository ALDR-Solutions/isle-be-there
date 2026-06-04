"""Security utilities for JWT authentication and password hashing."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings

# Shared OAuth2 scheme for bearer token endpoints.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def _encode_token(
    data: dict,
    secret_key: str,
    expires_at: datetime,
    token_type: str,
) -> str:
    payload = data.copy()
    payload.update({"exp": expires_at, "type": token_type})
    return jwt.encode(payload, secret_key, algorithm=settings.JWT_ALGORITHM)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return _encode_token(data, settings.get_jwt_secret_key(), expire, "access")


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    return _encode_token(data, settings.get_jwt_secret_key(), expire, "refresh")


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(
            token,
            settings.get_jwt_secret_key(),
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


def create_reset_password_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
        "type": "password_reset",
    }
    return jwt.encode(
        payload,
        settings.get_password_reset_secret_key(),
        settings.JWT_ALGORITHM,
    )


def decode_reset_password_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.get_password_reset_secret_key(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None
