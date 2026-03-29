from datetime import datetime
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
