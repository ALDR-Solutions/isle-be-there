from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.infrastructure.database import get_db
from sqlalchemy.orm import selectinload
from typing import List
from .schemas import (
    ItineraryEmailRequest,
    ItineraryUnsavedEmailRequest,
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItineraryItemResponse,
    ItineraryPriceItem,
    ItineraryPriceResponse,
    ItineraryResponse,
    ItineraryBookRequest,
    ItineraryConfirmResponse,
    ItinerarySaveRequest,
    SavedItineraryResponse,
    SavedItinerarySummaryResponse,
)
from .service import (
    plan_itinerary,
    confirm_itinerary,
    convert_itinerary_to_bookings,
    get_saved_itinerary,
    list_saved_itineraries,
    send_saved_itinerary_email,
    send_unsaved_itinerary_email,
    save_itinerary,
    delete_saved_itinerary,
)
from .models import Itinerary
from app.modules.users.models import User
from app.shared.dependencies.permissions import get_optional_current_user, require_roles
from app.modules.listings.models import Listing
import uuid

router = APIRouter(prefix="/api/itineraries", tags=["Itineraries"])


@router.post("/plan", response_model=ItineraryPlanResponse)
def plan_itinerary_endpoint(
    payload: ItineraryPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    return plan_itinerary(db, payload, current_user.id if current_user else None)


@router.post("", response_model=SavedItineraryResponse, status_code=201)
def create_itinerary_endpoint(
    payload: ItinerarySaveRequest,
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    return save_itinerary(db, current_user.id, payload)


@router.get("/{itinerary_id}", response_model=SavedItineraryResponse)
def get_itinerary_endpoint(
    itinerary_id: uuid.UUID,
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    return get_saved_itinerary(db, current_user.id, itinerary_id)


@router.post("/{itinerary_id}/email")
def email_itinerary_endpoint(
    itinerary_id: uuid.UUID,
    payload: ItineraryEmailRequest | None = None,
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    recipient = send_saved_itinerary_email(
        db,
        current_user.id,
        itinerary_id,
        payload.email if payload else None,
    )
    return {"detail": f"Itinerary sent to {recipient}."}

@router.post("/email")
def email_unsaved_itinerary_endpoint(
    payload: ItineraryUnsavedEmailRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    recipient = send_unsaved_itinerary_email(
        db,
        current_user.id if current_user else None,
        payload,
    )
    return {"detail": f"Itinerary sent to {recipient}."}



@router.get("", response_model=List[SavedItinerarySummaryResponse])
def list_itineraries_endpoint(
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    return list_saved_itineraries(db, current_user.id)


@router.delete("/{itinerary_id}")
def delete_itinerary_endpoint(
    itinerary_id: uuid.UUID,
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    delete_saved_itinerary(db, current_user.id, itinerary_id)
    return {"detail": "Itinerary deleted."}
