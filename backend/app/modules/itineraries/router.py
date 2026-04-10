from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.infrastructure.database import get_db

from .schemas import ItineraryPlanRequest, ItineraryPlanResponse
from .service import plan_itinerary

router = APIRouter(prefix="/api/itineraries", tags=["Itineraries"])


@router.post("/plan", response_model=ItineraryPlanResponse)
def plan_itinerary_endpoint(
    payload: ItineraryPlanRequest,
    db: Session = Depends(get_db),
):
    return plan_itinerary(db, payload)

