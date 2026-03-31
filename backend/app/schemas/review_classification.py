# Pydantic schemas for review classification
from pydantic import BaseModel, Field
from typing import Optional


class ClassificationRequest(BaseModel):
    """Request schema for review classification endpoint."""
    text: str = Field(..., description="Review text to classify")
    business_type_uuid: str = Field(
        ..., 
        description="UUID for business type: Hotel=390a6943-b75a-465b-a09b-560e7522682c, Restaurant=b155ad8f-91e8-4cee-9384-de3eb498bec5"
    )
    hotel_name: Optional[str] = Field(None, description="Optional business name")


class ClassificationResponse(BaseModel):
    """Response schema for review classification endpoint."""
    business_type_id: str
    business_type: str
    hotel_name: Optional[str] = None
    is_existing_business: bool
    detected_language: str
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    main_label: str
    second_label: str
    third_label: str
    
    class Config:
        from_attributes = True
