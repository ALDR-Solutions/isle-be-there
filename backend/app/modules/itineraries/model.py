from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, ForeignKey, SQLModel, Text
from sqlmodel import UUID as PGUUID


class ItineraryStatus(str, Enum):
    draft = "draft"
    saved = "saved"
    archived = "archived"


class Itinerary(SQLModel, table=True):
    __tablename__ = "itineraries"

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
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    title: str = Field(sa_column=Column(Text, nullable=False))
    start_date: date = Field(sa_column=Column(Date, nullable=False))
    end_date: date = Field(sa_column=Column(Date, nullable=False))
    status: ItineraryStatus = Field(
        default=ItineraryStatus.draft,
        sa_column=Column(Text, nullable=False, server_default=text("'draft'")),
    )
    budget_level: str = Field(sa_column=Column(Text, nullable=False))
    pace: str = Field(sa_column=Column(Text, nullable=False))

    total_budget: Optional[float] = Field(
        default=None, sa_column=Column(Float, nullable=True)
    )
    strict_budget: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    city: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    country: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    interests: Optional[list[str]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    preferred_business_types: Optional[list[str]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )

    total_estimated_cost: float = Field(
        default=0.0, sa_column=Column(Float, nullable=False, server_default=text("0"))
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
            onupdate=datetime.utcnow,
        )
    )


class ItineraryItem(SQLModel, table=True):
    __tablename__ = "itinerary_items"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    itinerary_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("itineraries.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )
    )
    listing_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("listings.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    linked_booking_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("bookings.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    item_type: str = Field(
        default="stop",
        sa_column=Column(Text, nullable=False, server_default=text("'stop'")),
    )
    title: str = Field(sa_column=Column(Text, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    day_date: date = Field(sa_column=Column(Date, nullable=False))
    start_at: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    end_at: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))

    sort_order: int = Field(
        default=0, sa_column=Column(Integer, nullable=False, server_default=text("0"))
    )
    estimated_cost: float = Field(
        default=0.0, sa_column=Column(Float, nullable=False, server_default=text("0"))
    )

    address_snapshot: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    reason_tags: Optional[list[str]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    extra_metadata: Optional[dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
            onupdate=datetime.utcnow,
        )
    )
