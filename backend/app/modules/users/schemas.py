from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    user_type: str = "regular"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    user_type: str | None = None
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


class ProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    avatar_url: str | None = None
    phone: str | None = None
    birth_date: datetime | None = None


class ProfileResponse(BaseModel):
    user_id: UUID
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    avatar_url: str | None = None
    phone: str | None = None
    birth_date: datetime | None = None
    interests_handled: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
