from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles

from .schemas import (
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItinerarySaveRequest,
    SavedItineraryResponse,
    SavedItinerarySummaryResponse,
)
from .service import (
    delete_saved_itinerary,
    get_saved_itinerary,
    list_saved_itineraries,
    plan_itinerary,
    save_itinerary,
)

router = APIRouter(prefix="/api/itineraries", tags=["Itineraries"])


@router.post("/plan", response_model=ItineraryPlanResponse)
def plan_itinerary_endpoint(
    payload: ItineraryPlanRequest,
    db: Session = Depends(get_db),
):
    return plan_itinerary(db, payload)


@router.get("", response_model=list[SavedItinerarySummaryResponse])
def list_saved_itineraries_endpoint(
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return list_saved_itineraries(db, current_user.id)


@router.post("", response_model=SavedItineraryResponse, status_code=status.HTTP_201_CREATED)
def save_itinerary_endpoint(
    payload: ItinerarySaveRequest,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return save_itinerary(db, current_user.id, payload)


@router.get("/{itinerary_id}", response_model=SavedItineraryResponse)
def get_saved_itinerary_endpoint(
    itinerary_id: UUID,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return get_saved_itinerary(db, current_user.id, itinerary_id)


@router.delete("/{itinerary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_itinerary_endpoint(
    itinerary_id: UUID,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    delete_saved_itinerary(db, current_user.id, itinerary_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

