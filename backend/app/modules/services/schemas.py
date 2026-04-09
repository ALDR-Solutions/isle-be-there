from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel


class RoomsJson(BaseModel):
    room_amenities: Optional[List[str]] = None
    room_type: Optional[str] = None


class MenuItemJson(BaseModel):
    menu_category: Optional[str] = None
    allergens: Optional[List[str]] = None


ServiceTypeData = Union[RoomsJson, MenuItemJson, Dict[str, Any]]


class ServiceBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    season_price: Optional[float] = None
    status: str | None = None
    capacity: Optional[int] = None
    availability: Optional[Dict[str, Any]] = None
    type_data: Optional[ServiceTypeData] = None
    listing_id: Optional[UUID] = None


class ServiceCreate(ServiceBase):
    status: str = "active"


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    season_price: Optional[float] = None
    status: str | None = None
    capacity: Optional[int] = None
    availability: Optional[Dict[str, Any]] = None
    type_data: Optional[Dict[str, Any]] = None


class ServiceResponse(ServiceBase):
    service_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}