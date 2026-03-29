from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BookingCreate(BaseModel):
    service_id: int
    booking_time: datetime
    status: Optional[str] = None
    user_id: Optional[UUID] = None


class BookingUpdate(BaseModel):
    booking_time: Optional[datetime] = None
    status: Optional[str] = None
