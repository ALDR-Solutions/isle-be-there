from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class InterestResponse(BaseModel):
    id: UUID
    name: str
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}


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

    model_config = {"from_attributes": True}
