from __future__ import annotations

from enum import Enum
from typing import List, Optional
from datetime import datetime, date

from sqlmodel import SQLModel, Field, Relationship


# Enums representing status values for itineraries and their items
class ItineraryStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ItineraryItemStatus(str, Enum):
    PLANNED = "planned"
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Itinerary(SQLModel):
    # Map to existing table
    __table__ = "itineraries"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    title: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ItineraryStatus] = None
    budget_level: Optional[str] = None
    pace: Optional[str] = None
    total_budget: Optional[float] = None
    strict_budget: Optional[bool] = None
    city: Optional[str] = None
    country: Optional[str] = None
    interests: Optional[str] = None
    preferred_business_types: Optional[str] = None
    total_estimated_cost: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # New columns
    applied_discount_id: Optional[int] = None
    discount_amount: Optional[float] = None

    # Relationships
    applied_discount_rel: Optional["Discount"] = Relationship(back_populates="itineraries")
    items: List["ItineraryItem"] = Relationship(back_populates="itinerary")
    user_rel: Optional["User"] = Relationship(back_populates="itineraries")


class ItineraryItem(SQLModel):
    # Map to existing table
    __table__ = "itinerary_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    itinerary_id: int = Field(foreign_key="itineraries.id")
    listing_id: int = Field(foreign_key="listings.id")
    linked_booking_id: Optional[int] = None
    item_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    day_date: Optional[date] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    sort_order: Optional[int] = None
    estimated_cost: Optional[float] = None
    address_snapshot: Optional[str] = None
    reason_tags: Optional[str] = None
    extra_metadata: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Relationships
    itinerary: Itinerary = Relationship(back_populates="items")
    listing_rel: "Listing" = Relationship(back_populates="itinerary_items")
    booking_rel: Optional["Booking"] = Relationship(back_populates="itinerary_item")
