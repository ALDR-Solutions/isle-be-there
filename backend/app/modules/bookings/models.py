from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Text, text, Numeric
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel, Relationship


class BookingStatus(str, Enum):
    pending = "pending"
    cancelled = "cancelled"
    approved = "approved"
    completed = "completed"


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    service_id: Optional[UUID] = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("services.service_id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=True,
        )
    )
    booking_from_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )
    booking_to_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), nullable=False),
    )
    status: Optional[BookingStatus] = Field(
        default=None,
        sa_column=Column(
            SAEnum(BookingStatus, name="booking_statuses", create_type=False),
            nullable=False,
            server_default=BookingStatus.pending.value,
        ),
    )
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
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
            onupdate=text("now()"),
        )
    )
    amount_of_people: int = Field(
        default=None, 
        sa_column=Column(
            Integer, 
            nullable=True,
            server_default=text("1")
        )
    )
    special_requests: Optional[str] = Field(
        default=None, 
        sa_column=Column(
            Text, 
            nullable=True
        )
    )
    bookers_name: str = Field(
        default=None, 
        sa_column=Column(
            Text, 
            nullable=True
        )
    )

    # Price-related fields (nullable defaults; populated at booking time)
    base_price: Optional[float] = Field(
        default=None,
        sa_column=Column(Numeric, nullable=True),
    )
    service_fee_percent: Optional[float] = Field(
        default=None,
        sa_column=Column(Numeric, nullable=True),
    )
    service_fee_amount: Optional[float] = Field(
        default=None,
        sa_column=Column(Numeric, nullable=True),
    )
    discount_percent: Optional[float] = Field(
        default=0,
        sa_column=Column(Numeric, nullable=True),
    )
    discount_amount: Optional[float] = Field(
        default=0,
        sa_column=Column(Numeric, nullable=True),
    )
    display_price: Optional[float] = Field(
        default=None,
        sa_column=Column(Numeric, nullable=True),
    )
    final_price: Optional[float] = Field(
        default=None,
        sa_column=Column(Numeric, nullable=True),
    )
    itinerary_item_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("itinerary_items.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    itinerary_item: Optional["ItineraryItem"] = Relationship(back_populates="booking_rel")
    stripe_payment_intent_id: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )


class PaymentEvent(SQLModel, table=True):
    __tablename__ = "payment_events"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    booking_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("bookings.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
    event_type: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    stripe_payment_intent_id: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    amount_cents: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )


