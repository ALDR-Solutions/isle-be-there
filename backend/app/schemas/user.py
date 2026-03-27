"""Pydantic schemas for auth / users."""
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_business: bool = False


class UserResponse(BaseModel):
    id: UUID
    email: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_business: bool | None = False
    is_super_admin: bool | None = False
    avatar_url: str | None = None
    phone: str | None = None
    birth_date: datetime | None = None
    interests_handled: bool | None = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ResetRequest(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    password: str
