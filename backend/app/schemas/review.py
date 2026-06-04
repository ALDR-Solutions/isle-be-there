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
    user_name: str | None = None
    rating: int
    comment: str | None = None
    censored_comment: str | None = None
    detected_language: str | None = None
    translated_comment: str | None = None
    main_label: str | None = None
    second_label: str | None = None
    third_label: str | None = None
    classification_labels: str | None = None
    classification_method: str | None = None
    created_at: datetime
    business_reply: "BusinessReplyResponse | None" = None

    model_config = {"from_attributes": True}


class ReviewSubmitResponse(BaseModel):
    id: UUID
    listing_id: UUID
    user_id: UUID
    rating: int
    comment: str | None = None
    censored_comment: str | None = None
    detected_language: str | None = None
    classification_labels: str | None = None
    main_label: str | None = None
    second_label: str | None = None
    third_label: str | None = None
    classification_method: str | None = None
    created_at: datetime
    detail: str | None = None

    model_config = {"from_attributes": True}


class BusinessReplyCreate(BaseModel):
    review_id: UUID
    description: str = Field(max_length=2000)


class BusinessReplyUpdate(BaseModel):
    description: str = Field(max_length=2000)


class BusinessReplyResponse(BaseModel):
    id: UUID
    review_id: UUID
    business_id: UUID
    user_id: UUID
    user_name: str | None = None
    description: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


ReviewResponse.model_rebuild()
