from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
from app.supabase_client import supabase

router = APIRouter(prefix="/api/ai", tags=["AI"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
class TravelRequest(BaseModel):
    destination: str
    preferences: str | None = None
    budget: str | None = None
    duration_days: int | None = 7
class RecommendationResponse(BaseModel):
    destinations: List[dict]
    tips: List[str]
def get_current_user_id(token: str) -> str:
    from app.core.security import decode_token
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None
@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: TravelRequest, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        return {"destinations": [], "tips": ["Please login to get recommendations"]}
    
    # Placeholder - integrate with OpenAI/Claude
    destinations = [
        {
            "name": request.destination or "Popular Destination",
            "description": "A wonderful place to visit",
            "best_time": "Spring or Fall",
            "estimated_cost": request.budget or "$1000-1500"
        }
    ]
    
    tips = [
        "Book accommodations in advance",
        "Check visa requirements",
        "Get travel insurance",
        "Learn basic local phrases"
    ]
    
    return RecommendationResponse(destinations=destinations, tips=tips)
@router.post("/itinerary")
async def generate_itinerary(destination: str, days: int, token: str = Depends(oauth2_scheme)):
    user_id = get_current_user_id(token)
    if not user_id:
        return {"error": "Please login"}
    
    itinerary = []
    for day in range(1, days + 1):
        itinerary.append({
            "day": day,
            "activities": [
                f"Morning: Explore local area",
                "Afternoon: Visit main attractions",
                "Evening: Try local cuisine"
            ]
        })
    
    return {
        "destination": destination,
        "days": days,
        "itinerary": itinerary
    }