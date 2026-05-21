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


class ReviewResponse(BaseModel):
    id: UUID
    listing_id: UUID
    user_id: UUID
    rating: int
    comment: str | None = None
    classification_labels: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewSubmitResponse(BaseModel):
    id: UUID
    listing_id: UUID
    user_id: UUID
    rating: int
    comment: str | None = None
    detected_language: str | None = None
    classification_labels: str | None = None
    main_label: str | None = None
    second_label: str | None = None
    third_label: str | None = None
    classification_method: str | None = None
    created_at: datetime
    detail: str | None = None

    model_config = {"from_attributes": True}
