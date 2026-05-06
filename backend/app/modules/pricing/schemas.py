from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class PlatformPricingConfigCreate(BaseModel):
    business_type_id: Optional[UUID]
    service_fee_percent: float
    is_active: bool = True
    effective_from: datetime
    effective_to: Optional[datetime]


class PlatformPricingConfigResponse(BaseModel):
    id: UUID
    business_type_id: Optional[UUID]
    service_fee_percent: float
    is_active: bool
    effective_from: datetime
    effective_to: Optional[datetime]
    model_config = {"from_attributes": True}


class ListingPriceResponse(BaseModel):
    listing_id: UUID
    base_price: float
    service_fee_percent: float
    service_fee_amount: float
    display_price: float
