from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    listing_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: int
    listing_id: UUID
    user_id: UUID
    rating: int
    comment: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    is_visible: bool = True

    model_config = {"from_attributes": True}


class ReviewClassifyRequest(BaseModel):
    """Request to classify a review text without saving."""
    text: str = Field(..., description="Review text to classify")
    business_type_uuid: str = Field(
        ..., 
        description="UUID for business type: Hotel, Restaurant, Events, Tours, Services"
    )
    hotel_name: str | None = Field(None, description="Optional business name")


class ReviewClassifyResponse(BaseModel):
    """Response with classification labels and flag status."""
    business_type_id: str
    business_type: str
    hotel_name: str | None = None
    main_label: str
    second_label: str
    third_label: str
    is_flagged: bool = False
    flag_reason: str | None = None
    detail: str | None = None

    model_config = {"from_attributes": True}


class ReviewSubmitRequest(BaseModel):
    """Request to submit a review with automatic classification."""
    listing_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    business_type_uuid: str = Field(
        ..., 
        description="UUID for business type: Hotel, Restaurant, Events, Tours, Services"
    )
    hotel_name: str | None = Field(None, description="Optional business name")


class ReviewSubmitResponse(BaseModel):
    """Response after submitting a review with classification."""
    id: int
    listing_id: UUID
    user_id: UUID
    rating: int
    comment: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    # Classification fields
    classification_labels: str | None = None  # JSON string of top 3 labels
    is_flagged: bool = False
    is_visible: bool = True
    flag_reason: str | None = None
    classified_at: datetime | None = None
    # Classification results
    business_type: str
    hotel_name: str | None = None
    main_label: str
    second_label: str
    third_label: str
    detail: str | None = None

    model_config = {"from_attributes": True}


class ReviewVisibilityUpdate(BaseModel):
    """Request to update review visibility (admin only)."""
    is_visible: bool = Field(..., description="New visibility value")

    model_config = {"from_attributes": True}
