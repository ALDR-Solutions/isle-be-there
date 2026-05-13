from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_booking_owner, require_roles

from .models import Booking
from .schemas import BookingCreate, BookingCreateResponse, BookingUpdate, BookingResponse, BookingPriceResponse, BulkBookingCreateRequest, BulkBookingCreateResponse
from .service import (
    cancel_booking,
    create_booking,
    create_bulk_bookings,
    get_booking_by_id,
    list_bookings,
    update_booking,
    price_booking_by_id,
)

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])




@router.get("", response_model=List[BookingResponse])
def get_bookings(
    current_user: User = Depends(require_roles("regular", "admin")),
    db: Session = Depends(get_db),
):
    return list_bookings(db, current_user.id)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    current_user: User = Depends(require_roles("regular", "admin")),
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    return get_booking_by_id(db, booking.id, current_user.id)




@router.post("", response_model=BookingCreateResponse, status_code=201)
def create_booking_endpoint(
    booking_data: BookingCreate,
    current_user: User = Depends(require_roles("regular")),
    db: Session = Depends(get_db),
):
    return create_booking(db, booking_data, current_user.id)


@router.post("/bulk", response_model=BulkBookingCreateResponse, status_code=201)
def create_bulk_bookings_endpoint(
    request: BulkBookingCreateRequest,
    current_user: User = Depends(require_roles("regular")),
    db: Session = Depends(get_db),
):
    bookings = create_bulk_bookings(db, request.items, current_user.id)
    return BulkBookingCreateResponse(
        bookings=[BookingCreateResponse.model_validate(b) for b in bookings]
    )


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking_endpoint(
    booking_data: BookingUpdate,
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    
    update_data = booking_data.model_dump(exclude_unset=True)

    return update_booking(db, booking, update_data)


@router.post("/{booking_id}/cancel", status_code=204)
def cancel_booking_endpoint(
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):

    cancel_booking(db, booking)
    return Response(status_code=204)

@router.get("/{booking_id}/price", response_model=BookingPriceResponse)
def get_booking_price_endpoint(
    current_user: User = Depends(require_roles("regular", "admin")),
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    price = price_booking_by_id(db, booking.id, current_user.id)
    return BookingPriceResponse(**price)
