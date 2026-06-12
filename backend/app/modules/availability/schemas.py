from datetime import date, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class SlotAvailability(BaseModel):
    """Individual slot availability with remaining capacity."""

    slot_id: int
    day_of_week: int
    start_time: time
    end_time: time
    capacity: int
    remaining_capacity: int
    is_available: bool


class ServiceAvailableResponse(BaseModel):
    """Response for service availability query."""

    service_id: UUID
    date: str  # ISO format date
    day_of_week: int
    is_available: bool
    is_open: bool
    slots: list[SlotAvailability]
    closed_reason: Optional[str] = None


class BulkServiceAvailabilityRequestItem(BaseModel):
    key: str
    service_id: UUID
    date: date
    people: int = Field(default=1, ge=1)


class BulkServiceAvailabilityRequest(BaseModel):
    requests: list[BulkServiceAvailabilityRequestItem]


class BulkServiceAvailabilityResult(BaseModel):
    key: str
    availability: ServiceAvailableResponse


class BulkServiceAvailabilityResponse(BaseModel):
    results: list[BulkServiceAvailabilityResult]


class MassAvailabilityItem(BaseModel):
    """Individual date availability for mass endpoint."""

    date: str
    is_open: bool


class MassAvailabilityResponse(BaseModel):
    """Response for mass availability query (lightweight, no slot details)."""

    service_id: UUID
    start_date: str
    end_date: str
    availability: list[MassAvailabilityItem]


class ListingHoursBase(BaseModel):
    day_of_week: int = Field(ge=0, le=6, description="0=Sunday, 6=Saturday")
    open_time: time
    close_time: time

    @model_validator(mode="after")
    def validate_times(self):
        if self.open_time >= self.close_time:
            raise ValueError("open_time must be before close_time")
        return self


class ListingHoursCreate(ListingHoursBase):
    listing_id: UUID


class ListingHoursUpdate(BaseModel):
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    open_time: Optional[time] = None
    close_time: Optional[time] = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.open_time is not None and self.close_time is not None:
            if self.open_time >= self.close_time:
                raise ValueError("open_time must be before close_time")
        return self


class ListingHoursResponse(ListingHoursBase):
    id: int
    listing_id: UUID


class ServiceSlotsBase(BaseModel):
    day_of_week: int = Field(ge=0, le=6, description="0=Sunday, 6=Saturday")
    start_time: time
    end_time: time
    capacity: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        return self


class ServiceSlotsCreate(ServiceSlotsBase):
    service_id: UUID


class ServiceSlotsUpdate(BaseModel):
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    capacity: Optional[int] = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_times(self):
        if self.start_time is not None and self.end_time is not None:
            if self.start_time >= self.end_time:
                raise ValueError("start_time must be before end_time")
        return self


class ServiceSlotsResponse(ServiceSlotsBase):
    id: int
    service_id: UUID
