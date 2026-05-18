from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from app.modules.services.models import StatusTypes


class RoomsJson(BaseModel):
    room_amenities: Optional[List[str]] = None
    room_type: Optional[str] = None


ServiceTypeData = Union[RoomsJson, Dict[str, Any]]


class ServiceBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    season_price: Optional[float] = None
    status: Optional[StatusTypes] = None
    capacity: Optional[int] = None
    availability: Optional[Dict[str, Any]] = None
    type_data: Optional[ServiceTypeData] = None
    listing_id: Optional[UUID] = None


class ServiceCreate(ServiceBase):
    status: StatusTypes = StatusTypes.active


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    season_price: Optional[float] = None
    status: Optional[StatusTypes] = None
    capacity: Optional[int] = None
    availability: Optional[Dict[str, Any]] = None
    type_data: Optional[Dict[str, Any]] = None


class ServiceResponse(ServiceBase):
    service_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

