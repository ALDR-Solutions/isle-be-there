from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Column, BigInteger, Float, DateTime, ForeignKey, Text, Identity, text, Boolean, SmallInteger
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlmodel import Field, Relationship, SQLModel

from app.modules.listings.models import Listing


class Service(SQLModel, table=True):
    __tablename__ = "services"

    service_id: int = Field(
        sa_column=Column(
            BigInteger,
            Identity(always=False, start=1, increment=1),
            primary_key=True,
            nullable=False,
            autoincrement=True,
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
    status: Optional[bool] = Field(default=None, sa_column=Column(Boolean, nullable=True))
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
    listing_rel: Optional["Listing"] = Relationship(back_populates="services")