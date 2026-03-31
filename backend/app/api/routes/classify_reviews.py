# Review Classification API routes
from fastapi import APIRouter, HTTPException

from app.schemas.review_classification import ClassificationRequest, ClassificationResponse
from app.services.review_classifier import classify_review

router = APIRouter(prefix="/api/reviews", tags=["Review Classification"])


@router.post("/classify", response_model=ClassificationResponse)
async def classify_review_endpoint(request: ClassificationRequest):
    """
    Classify a review based on business type.
    
    Supports:
    - Hotels (business_type_uuid=390a6943-b75a-465b-a09b-560e7522682c): room, service, food, clean, location, amenities, value, other
    - Restaurants (business_type_uuid=b155ad8f-91e8-4cee-9384-de3eb498bec5): food_quality, service_quality, ambience, cleanliness, 
      value_for_money, location_convenience, wait_time, hygiene_safety, dietary_options
    
    Multi-language support: English, French, Spanish, Dutch
    """
    try:
        result = classify_review(
            text=request.text,
            business_type_uuid=request.business_type_uuid,
            hotel_name=request.hotel_name,
            verbose=False
        )
        
        # Check for errors in result
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
