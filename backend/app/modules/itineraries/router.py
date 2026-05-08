from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.infrastructure.database import get_db
from sqlalchemy.orm import selectinload
from typing import List, Optional
from .schemas import (
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItineraryItemCreate,
    ItineraryItemResponse,
    ItineraryPriceItem,
    ItineraryPriceResponse,
    ItineraryResponse,
    ItineraryBookRequest,
    ItineraryConfirmResponse,
)
from .service import plan_itinerary, create_itinerary, get_itinerary_by_id, confirm_itinerary, convert_itinerary_to_bookings
from .models import Itinerary
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles
from app.modules.listings.models import Listing
import uuid
from datetime import date
from pydantic import BaseModel

router = APIRouter(prefix="/api/itineraries", tags=["Itineraries"])


@router.post("/plan", response_model=ItineraryPlanResponse)
def plan_itinerary_endpoint(
    payload: ItineraryPlanRequest,
    db: Session = Depends(get_db),
):
    return plan_itinerary(db, payload)


class ItineraryCreateRequest(BaseModel):
    title: Optional[str] = None
    budget_level: Optional[str] = None
    pace: Optional[str] = None
    strict_budget: Optional[bool] = None
    start_date: date
    end_date: date
    items: List[ItineraryItemCreate]


@router.post("", response_model=ItineraryResponse, status_code=201)
def create_itinerary_endpoint(
    payload: ItineraryCreateRequest,
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    data = {
        "title": payload.title,
        "budget_level": payload.budget_level,
        "pace": payload.pace,
        "strict_budget": payload.strict_budget,
        "start_date": payload.start_date,
        "end_date": payload.end_date,
        "items": [item.dict() for item in payload.items],
    }
    return create_itinerary(db, current_user.id, data)


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
def get_itinerary_endpoint(
    itinerary_id: uuid.UUID,
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    itinerary = get_itinerary_by_id(db, itinerary_id, current_user.id)
    response_items = [
        ItineraryItemResponse(
            id=item.id,
            listing_id=item.listing_id,
            booking={"id": str(item.linked_booking_id)} if item.linked_booking_id else None,
        )
        for item in itinerary.items
    ]
    return ItineraryResponse(id=itinerary.id, applied_discount=None, items=response_items)


@router.get("/{itinerary_id}/price", response_model=ItineraryPriceResponse)
def itinerary_price_endpoint(itinerary_id: uuid.UUID, db: Session = Depends(get_db)):
    itinerary = db.exec(
        select(Itinerary).where(Itinerary.id == itinerary_id).options(selectinload(Itinerary.items))
    ).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    price_items: list[ItineraryPriceItem] = []
    subtotal = 0.0
    for item in itinerary.items or []:
        listing = db.exec(select(Listing).where(Listing.id == item.listing_id)).first()
        title = listing.title if listing else ""
        business_type_name = (
            (listing.business_type_rel.name if listing and listing.business_type_rel else "unknown").lower()
            if listing
            else "unknown"
        )
        est_cost = float(getattr(item, "estimated_cost", 0.0))
        price_items.append(
            ItineraryPriceItem(
                listing_id=item.listing_id,
                title=title,
                business_type_name=business_type_name,
                estimated_cost=est_cost,
            )
        )
        subtotal += est_cost

    service_fee = 0.0
    discount = 0.0
    total = subtotal + service_fee - discount
    return ItineraryPriceResponse(
        items=price_items,
        subtotal=subtotal,
        service_fee=service_fee,
        discount=discount,
        total=total,
    )


@router.post("/{itinerary_id}/confirm", response_model=ItineraryConfirmResponse)
def itinerary_confirm_endpoint(
    itinerary_id: uuid.UUID,
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    result = confirm_itinerary(db, itinerary_id, current_user.id)
    itinerary = result["itinerary"]
    # Convert ORM items to response objects
    response_items = [
        ItineraryItemResponse(
            id=item.id,
            listing_id=item.listing_id,
            booking={"id": str(item.linked_booking_id)} if item.linked_booking_id else None,
        )
        for item in itinerary.items
    ]
    # Build ItineraryResponse from ORM object
    response_itinerary = ItineraryResponse(
        id=itinerary.id,
        applied_discount=None,  # May be populated via discount_id if available
        items=response_items,
    )
    return ItineraryConfirmResponse(
        itinerary=response_itinerary,
        discount_applied=result.get("discount_applied", False),
        discount_amount=result.get("discount_amount", 0.0),
    )


@router.post("/{itinerary_id}/book", response_model=ItineraryResponse)
def itinerary_book_endpoint(
    itinerary_id: uuid.UUID,
    payload: ItineraryBookRequest,
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    updated_itinerary = convert_itinerary_to_bookings(
        db, itinerary_id, current_user.id, payload.item_ids
    )
    response_items = [
        ItineraryItemResponse(
            id=item.id,
            listing_id=item.listing_id,
            booking={"id": str(item.linked_booking_id)} if item.linked_booking_id else None,
        )
        for item in updated_itinerary.items
    ]
    return ItineraryResponse(id=updated_itinerary.id, applied_discount=None, items=response_items)


@router.get("", response_model=List[ItineraryResponse])
def list_itineraries_endpoint(
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    itineraries = db.exec(
        select(Itinerary).where(Itinerary.user_id == current_user.id).options(selectinload(Itinerary.items))
    ).all()
    result = []
    for i in itineraries:
        response_items = [
            ItineraryItemResponse(
                id=item.id,
                listing_id=item.listing_id,
                booking={"id": str(item.linked_booking_id)} if item.linked_booking_id else None,
            )
            for item in i.items
        ]
        result.append(ItineraryResponse(id=i.id, applied_discount=None, items=response_items))
    return result

