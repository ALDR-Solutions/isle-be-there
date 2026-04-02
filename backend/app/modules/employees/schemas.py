from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str
    business_id: UUID | None = None


class EmployeeResponse(BaseModel):
    id: UUID
    email: EmailStr
    business_id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}