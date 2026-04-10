from datetime import datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from .models import Statuses


class _StrictDetailsBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def _require_at_least_one_field(self):
        if not any(v is not None for v in self.model_dump().values()):
            raise ValueError("details must include at least one field")
        return self


class HotelListingJson(_StrictDetailsBase):
    room_count: Optional[int] = None
    star_level: Optional[int] = None
    hotel_amenities: Optional[List[str]] = None
    cancellation_until_hours: Optional[int] = None
    deposit_required: Optional[bool] = None
    total_rooms: Optional[int] = None
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None


class TourListingJson(_StrictDetailsBase):
    duration: Optional[float] = None
    available_days: Optional[List[str]] = None
    max_capacity: Optional[int] = None
    service_availability: Optional[str] = None


class RestaurantListingJson(_StrictDetailsBase):
    table_seating: Optional[bool] = None
    has_delivery: Optional[bool] = None
    has_take_out: Optional[bool] = None
    has_dining: Optional[bool] = None
    service_availability: Optional[str] = None
    menu_items: Optional[List[str]] = None


class ActivityListingJson(_StrictDetailsBase):
    estimated_duration: Optional[float] = None
    available_days: Optional[List[str]] = None
    is_indoor: Optional[bool] = None
    difficulty_level: Optional[str] = None


BUSINESS_TYPE_DETAILS_MAP = {
    "hotel": HotelListingJson,
    "tour": TourListingJson,
    "restaurant": RestaurantListingJson,
    "activity": ActivityListingJson,
}


def validate_details(business_type_name: str, details: dict) -> dict:
    model = BUSINESS_TYPE_DETAILS_MAP.get(business_type_name.lower())
    if not model:
        raise ValueError(f"Unknown business type: {business_type_name}")
    validated = model(**details)
    return validated.model_dump(exclude_none=True)


class ListingBase(BaseModel):
    business_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    base_price: Optional[float] = None
    business_type: Optional[UUID] = None
    image_urls: Optional[List[str]] = None
    status: Optional[Statuses] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class ListingLocation(BaseModel):
    lat: float
    lng: float


class ListingCreate(ListingBase):
    location: Optional[ListingLocation] = None
    status: Statuses = Statuses.pending


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    base_price: Optional[float] = None
    image_urls: Optional[List[str]] = None
    status: Optional[Statuses] = None
    phone_number: Optional[str] = None
    email_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    location: Optional[ListingLocation] = None


class ListingResponse(ListingBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    location: Optional[ListingLocation] = None
    avg_rating: Optional[float] = None
    review_count: int = 0
    business_type_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
