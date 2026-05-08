from enum import Enum
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from pydantic import Json
from sqlmodel import Date, SQLModel, Field, Relationship, text
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, Text, text, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from app.modules.users.models import User
from app.modules.listings.models import Listing
from app.modules.bookings.models import Booking


def _enum_values(enum_cls: type[Enum]) -> list[str]:
    return [member.value for member in enum_cls]


# Enums representing status values for itineraries and their items
class ItineraryStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    SAVED = "saved"
    ARCHIVED = "archived"


class ItineraryItemStatus(str, Enum):
    PLANNED = "planned"
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Itinerary(SQLModel, table=True):
    # Map to existing table
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
            ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
    title: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    start_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    end_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    status: Optional[ItineraryStatus] = Field(
        default=None,
        sa_column=Column(
            SAEnum(ItineraryStatus, values_callable=_enum_values),
            nullable=True,
        ),
    )
    budget_level: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    pace: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    total_budget: Optional[float] = Field(default=None, sa_column=Column(Numeric(precision=10, scale=2), nullable=True))
    strict_budget: Optional[bool] = Field(default=None, sa_column=Column(Boolean, nullable=True))
    city: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    country: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    interests: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    preferred_business_types: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    total_estimated_cost: Optional[float] = Field(default=None, sa_column=Column(Numeric(precision=10, scale=2), nullable=True))
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
        )
    )

    # New columns
    applied_discount_id: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    discount_amount: Optional[float] = Field(default=None, sa_column=Column(Numeric(precision=10, scale=2), nullable=True))

    # Relationships - use Mapped types directly (class already imported)
    items: Mapped[List["ItineraryItem"]] = Relationship(back_populates="itinerary")
    user_rel: Mapped["User"] = Relationship(back_populates="itineraries")


class ItineraryItem(SQLModel, table=True):
    # Map to existing table
    __tablename__ = "itinerary_items"

    id: UUID = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        ),
    )
    itinerary_id: UUID = Field(foreign_key="itineraries.id")
    listing_id: UUID = Field(foreign_key="listings.id")
    linked_booking_id: Optional[UUID] = Field(default=None, sa_column=Column(PGUUID(as_uuid=True), nullable=True))
    item_type: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    title: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    day_date: Optional[date] = Field(default=None, sa_column=Column(Date, nullable=True))
    start_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
    end_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime, nullable=True))
    sort_order: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    estimated_cost: Optional[float] = Field(default=None, sa_column=Column(Numeric(precision=10, scale=2), nullable=True))
    address_snapshot: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    reason_tags: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    extra_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
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
        )
    )

    # Relationships - use Mapped types directly (class already imported)
    itinerary: Mapped["Itinerary"] = Relationship(back_populates="items")
    listing_rel: Mapped["Listing"] = Relationship(back_populates="itinerary_items")
    booking_rel: Mapped[Optional["Booking"]] = Relationship(back_populates="itinerary_item")
