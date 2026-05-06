from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.modules.bookings.models import BookingStatus



class BookingBase(BaseModel):
    status: Optional[BookingStatus] = BookingStatus.pending
    user_id: Optional[UUID] = None
    amount_of_people: Optional[int] = 1
    bookers_name: str = None
    special_requests: Optional[str] = None
    booking_from_time: Optional[datetime] = None
    booking_to_time: Optional[datetime] = None




class BookingCreate(BookingBase):
    status: BookingStatus = BookingStatus.pending
    service_id: Optional[UUID] = None
    listing_id: Optional[UUID] = None


class BookingUpdate(BaseModel):
    amount_of_people: Optional[int] = 1
    bookers_name: Optional[str] = None
    booking_from_time: Optional[datetime] = None
    booking_to_time: Optional[datetime] = None
    special_requests: Optional[str] = None
    status: Optional[BookingStatus] = None

class BookingResponse(BaseModel):
    id: UUID
    bookers_name: str
    amount_of_people: int
    special_requests: Optional[str]
    booking_from_time: datetime
    booking_to_time: datetime
    service_id: Optional[UUID] = None
    listing_id: Optional[UUID] = None
    service_name: Optional[str] = None
    listing_name: Optional[str] = None
    status: Optional[BookingStatus] = None
    created_at: datetime
    updated_at: datetime

class BookingCreateResponse(BaseModel):
    id: UUID
    bookers_name: str
    amount_of_people: int
    special_requests: Optional[str]
    booking_from_time: datetime
    booking_to_time: datetime
    service_id: Optional[UUID] = None
    listing_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
