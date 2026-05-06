from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field
from app.modules.discounts.models import DiscountType


class DiscountCreate(BaseModel):
    name: str
    discount_type: DiscountType
    discount_percent: float = Field(
        ..., ge=0.01, le=0.50,
        description="Discount percent as a fraction (e.g., 0.20 for 20%)",
    )
    min_services: Optional[int] = None
    required_business_types: Optional[List[str]] = None
    min_total_cost: Optional[float] = None
    max_discount_amount: Optional[float] = None
    is_active: bool = True
    valid_from: datetime
    valid_to: Optional[datetime] = None
    max_uses: Optional[int] = None
    description: Optional[str] = None


class DiscountUpdate(BaseModel):
    name: Optional[str] = None
    discount_type: Optional[DiscountType] = None
    discount_percent: Optional[float] = Field(None, ge=0.01, le=0.50)
    min_services: Optional[int] = None
    required_business_types: Optional[List[str]] = None
    min_total_cost: Optional[float] = None
    max_discount_amount: Optional[float] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    max_uses: Optional[int] = None
    description: Optional[str] = None


class DiscountResponse(BaseModel):
    id: int
    name: str
    discount_type: DiscountType
    discount_percent: float
    min_services: Optional[int] = None
    required_business_types: Optional[List[str]] = None
    min_total_cost: Optional[float] = None
    max_discount_amount: Optional[float] = None
    is_active: bool
    valid_from: datetime
    valid_to: Optional[datetime] = None
    max_uses: Optional[int] = None
    description: Optional[str] = None
    current_uses: int

    # Allow ORMs/attributes to populate this response
    model_config = {"from_attributes": True}


class DiscountEligibilityResponse(BaseModel):
    discount: DiscountResponse
    eligible: bool
    reason: Optional[str] = None
    estimated_discount: Optional[float] = None
