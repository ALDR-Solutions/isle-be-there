"""Pydantic schemas for listings."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel


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

    class Config:
        from_attributes = True
