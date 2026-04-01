from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    season_price: Optional[float] = None
    status: Optional[bool] = None
    capacity: Optional[int] = None
    availability: Optional[Dict[str, Any]] = None
    type_data: Optional[Dict[str, Any]] = None
    listing_id: Optional[UUID] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    season_price: Optional[float] = None
    status: Optional[bool] = None
    capacity: Optional[int] = None
    availability: Optional[Dict[str, Any]] = None
    type_data: Optional[Dict[str, Any]] = None
    listing_id: Optional[UUID] = None


class ServiceResponse(ServiceBase):
    service_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}