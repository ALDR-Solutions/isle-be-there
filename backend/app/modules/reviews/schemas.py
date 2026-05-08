from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    listing_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5000)


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5000)
    user_id: UUID | None = None


class ReviewSubmitRequest(BaseModel):
    listing_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=5000)


class ReviewSubmitResponse(BaseModel):
    id: UUID
    listing_id: UUID
    user_id: UUID
    rating: int
    comment: str | None = None
    censored_comment: str | None = None
    detected_language: str | None = None
    classification_labels: str | None = None
    created_at: datetime
    detail: str | None = None

    model_config = {"from_attributes": True}


class BusinessReplyCreate(BaseModel):
    description: str = Field(..., description="Reply text")


class BusinessReplyResponse(BaseModel):
    id: int
    review_id: UUID
    business_id: str | None = None
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}
