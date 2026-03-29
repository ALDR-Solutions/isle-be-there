from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BusinessBase(BaseModel):
    business_name: str
    description: Optional[str] = None
    business_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: Optional[bool] = False
    user_id: Optional[UUID] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    business_name: Optional[str] = None
    description: Optional[str] = None
    business_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
