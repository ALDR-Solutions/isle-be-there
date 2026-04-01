from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Identity, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel


class BookingStatus(str, Enum):
    pending = "pending"
    cancelled = "cancelled"
    approved = "approved"
    completed = "completed"


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: int = Field(
        sa_column=Column(
            BigInteger,
            Identity(always=False, start=1, increment=1),
            primary_key=True,
            nullable=False,
            autoincrement=True,
        )
    )
    service_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("services.service_id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=True,
        )
    )
    booking_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), nullable=True),
    )
    status: Optional[BookingStatus] = Field(
        default=None,
        sa_column=Column(
            SAEnum(BookingStatus, name="booking_statuses", create_type=False),
            nullable=True,
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
