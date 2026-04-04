from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel


class HotelListingJson(BaseModel):
    room_count: Optional[int] = None
    star_level: Optional[int] = None
    hotel_amenities: Optional[List[str]] = None
    cancellation_until_hours: Optional[int] = None
    deposit_required: Optional[bool] = None
    total_rooms: Optional[int] = None
    available_rooms: Optional[int] = None


class TourListingJson(BaseModel):
    duration: Optional[float] = None
    available_days: Optional[List[str]] = None
    max_capacity: Optional[int] = None
    available_slots: Optional[int] = None
    service_availability: Optional[str] = None


class RestaurantListingJson(BaseModel):
    table_seating: Optional[bool] = None
    has_delivery: Optional[bool] = None
    has_take_out: Optional[bool] = None
    has_dining: Optional[bool] = None
    service_availability: Optional[str] = None


class ActivityListingJson(BaseModel):
    estimated_duration: Optional[float] = None
    available_days: Optional[List[str]] = None
    is_indoor: Optional[bool] = None
    difficulty_level: Optional[str] = None


ListingDetails = Union[
    HotelListingJson,
    TourListingJson,
    RestaurantListingJson,
    ActivityListingJson,
    Dict[str, Any],
]


class ListingBase(BaseModel):
    business_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    base_price: Optional[float] = None
    business_type: Optional[UUID] = None
    image_urls: Optional[List[str]] = None
    status: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    location: Optional[str] = None
    details: Optional[ListingDetails] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    business_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    base_price: Optional[float] = None
    business_type: Optional[UUID] = None
    image_urls: Optional[List[str]] = None
    status: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    location: Optional[str] = None
    details: Optional[ListingDetails] = None


class ListingLocation(BaseModel):
    lat: float
    lng: float


class ListingResponse(ListingBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    location: Optional[ListingLocation] = None
    avg_rating: Optional[float] = None
    review_count: int = 0
    business_type_name: Optional[str] = None

    model_config = {"from_attributes": True}
