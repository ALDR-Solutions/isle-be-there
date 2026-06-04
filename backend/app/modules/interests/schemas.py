from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InterestResponse(BaseModel):
    id: UUID
    name: str
    category: str
    category_id: UUID
    created_at: datetime


class InterestCategoryResponse(BaseModel):
    name: str
    description: str


class ItineraryInterestsResponse(BaseModel):
    categories: list[InterestCategoryResponse]
    interests: list[InterestResponse]


class UserInterestsUpdate(BaseModel):
    interest_ids: list[UUID]


class BusinessTypeInterestBase(BaseModel):
    business_type_id: UUID
    interest_id: UUID


class BusinessTypeInterestCreate(BusinessTypeInterestBase):
    pass


class BusinessTypeInterestUpdate(BaseModel):
    business_type_id: Optional[UUID] = None
    interest_id: Optional[UUID] = None


class BusinessTypeInterestResponse(BusinessTypeInterestBase):
    created_at: datetime
