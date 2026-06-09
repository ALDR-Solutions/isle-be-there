from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from geoalchemy2 import Geography
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, Relationship, SQLModel

from app.modules.listings.models import Listing


class Business(SQLModel, table=True):
    __tablename__ = "businesses"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    business_name: str = Field(sa_column=Column(Text, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    business_email: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    phone: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    address: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    website: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    logo_url: Optional[str] = Field(default=None, sa_column=Column(String, nullable=True))
    is_verified: Optional[bool] = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )
    user_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    location: Optional[Any] = Field(
        default=None,
        sa_column=Column(Geography, nullable=True),
    )

    listings: list["Listing"] = Relationship(back_populates="business_rel")


class BusinessType(SQLModel, table=True):
    __tablename__ = "business_types"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )
    name: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    listings: list["Listing"] = Relationship(back_populates="business_type_rel")
