from uuid import UUID
from datetime import datetime, date
from typing import Optional

from sqlalchemy import Column, Date, DateTime, Boolean, ForeignKey, Text, text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel, Relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Profile(SQLModel, table=True):
    __tablename__ = "profiles"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )

    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
            unique=True,
            nullable=False,
        )
    )

    avatar_url: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    phone: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    first_name: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    last_name: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    birth_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text("now()")),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text("now()")),
    )

    interests_handled: Optional[bool] = Field(
        default=False,
        sa_column=Column(Boolean, nullable=True, server_default=text("false")),
    )

    user: "User" = Relationship(back_populates="profile")
