from datetime import time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


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
    capacity: int = Field(default=1, ge=1)


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