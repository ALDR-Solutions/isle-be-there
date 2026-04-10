from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel



class BookingBase(BaseModel):
    status: Optional[str] = "pending"
    user_id: Optional[UUID] = None
    amount_of_people: Optional[int] = 1
    bookers_name: str = None
    special_requests: Optional[str] = None
    booking_from_time: Optional[datetime] = None
    booking_to_time: Optional[datetime] = None




class BookingCreate(BookingBase):
    status: str = "pending"
    service_id: Optional[UUID] = None


class BookingUpdate(BaseModel):
    amount_of_people: Optional[int] = None
    bookers_name: str = None
    booking_from_time: Optional[datetime] = None
    booking_to_time: Optional[datetime] = None
    special_requests: Optional[str] = None
    status: Optional[str] = "pending"
