from datetime import date, datetime
from typing import Optional
from uuid import UUID
from enum import Enum
from sqlmodel import (
    Field,
    SQLModel,
    Enum as SAEnum,
    text,
    UUID as PGUUID,
    Column,
    Boolean,
    Text,
    DateTime,
)


class UserTypes(str, Enum):
    regular = "regular"
    business = "business"
    admin = "admin"
    employee = "employee"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    email: str = Field(sa_column=Column(Text, unique=True, nullable=False, index=True))
    hashed_password: str = Field(sa_column=Column(Text, nullable=False))
    username: Optional[str] = Field(
        default=None, sa_column=Column(Text, unique=True, nullable=True)
    )
    first_name: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    last_name: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    user_type: UserTypes = Field(
        default=UserTypes.regular,
        sa_column=Column(
            SAEnum(UserTypes), nullable=False, server_default=text("'regular'")
        ),
    )
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    is_verified: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    verification_token: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    avatar_url: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    phone: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    birth_date: Optional[date] = Field(default=None)
    interests_handled: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        )
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
