from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CalendarEventResponse(BaseModel):
    id: str
    source: str
    title: str
    start: datetime
    end: datetime
    status: str
    color: str
    details: dict = Field(default_factory=dict)
    listing_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None
    itinerary_id: Optional[UUID] = None
    itinerary_item_id: Optional[UUID] = None
