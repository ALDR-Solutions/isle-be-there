"""Pydantic schemas for bookings."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from uuid import UUID


class BookingCreate(BaseModel):
    service_id: int
    booking_time: datetime
    status: Optional[str] = None
    user_id: Optional[UUID] = None


class BookingUpdate(BaseModel):
    booking_time: Optional[datetime] = None
    status: Optional[str] = None
