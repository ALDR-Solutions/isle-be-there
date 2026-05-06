from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_booking_owner, require_roles

from .models import Booking
from .schemas import BookingCreate, BookingCreateResponse, BookingUpdate, BookingResponse
from .service import (
    cancel_booking,
    create_booking,
    get_booking_by_id,
    list_bookings,
    update_booking,
)

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])




@router.get("", response_model=List[BookingResponse])
def get_bookings(
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return list_bookings(db, current_user.id)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    current_user: User = Depends(require_roles("user", "admin")),
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    return get_booking_by_id(db, booking.id, current_user.id)




@router.post("", response_model=BookingCreateResponse, status_code=201)
def create_booking_endpoint(
    booking_data: BookingCreate,
    current_user: User = Depends(require_roles("user")),
    db: Session = Depends(get_db),
):
    return create_booking(db, booking_data, current_user.id)


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
    
