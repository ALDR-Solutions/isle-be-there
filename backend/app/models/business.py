from uuid import UUID
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Column, DateTime, Text, String, Float, Boolean, ForeignKey, text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .listing import Listing


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

    latitude: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))
    longitude: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))

    listings: List["Listing"] = Relationship(back_populates="business_rel")
