from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Column, BigInteger, Float, DateTime, ForeignKey, Text, Identity, text, Boolean, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlmodel import Enum as SAEnum, Field, Relationship, SQLModel
from enum import Enum

from app.modules.listings.models import Listing


class StatusTypes(str, Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class Service(SQLModel, table=True):
    __tablename__ = "services"

    service_id: UUID = Field(
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
            server_default="now()",
        )
    )
    name: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    price: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))
    season_price: Optional[float] = Field(default=None, sa_column=Column(Float, nullable=True))
    status: StatusTypes = Field(
        default=StatusTypes.active,
        sa_column=Column(
            SAEnum(StatusTypes, name="status_types"),
            nullable=False,
            server_default=text("'active'"),
        ),
    )
    capacity: Optional[int] = Field(default=None, sa_column=Column(SmallInteger, nullable=True))
    availability: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    type_data: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), nullable=True),
    )
    listing_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("listings.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    # listing_rel: Optional["Listing"] = Relationship(back_populates="services")