from datetime import datetime
from typing import List, Optional
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
    itinerary_item_id: Optional[UUID] = None




class BookingCreate(BookingBase):
    status: BookingStatus = BookingStatus.pending
    service_id: Optional[UUID] = None
    base_price: Optional[float] = None


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
    service_name: Optional[str] = None
    listing_name: Optional[str] = None
    status: Optional[BookingStatus] = None
    created_at: datetime
    updated_at: datetime
    # Price fields (calculated server-side)
    base_price: Optional[float] = None
    service_fee_percent: Optional[float] = None
    service_fee_amount: Optional[float] = None
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    display_price: Optional[float] = None
    final_price: Optional[float] = None
    model_config = {"from_attributes": True}


class BookingPriceResponse(BaseModel):
    base_price: float
    service_fee_percent: float
    service_fee_amount: float
    discount_percent: float
    discount_amount: float
    display_price: float
    final_price: float

class BookingCreateResponse(BaseModel):
    id: UUID
    bookers_name: str
    amount_of_people: int
    special_requests: Optional[str]
    booking_from_time: datetime
    booking_to_time: datetime
    service_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class BulkBookingCreateRequest(BaseModel):
    items: List[BookingCreate]


class BulkBookingCreateResponse(BaseModel):
    bookings: List[BookingCreateResponse]
