from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, Integer, Text, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False))
    service_id: int = Field(sa_column=Column(Integer, nullable=False))
    booking_time: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    status: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        )
    )
