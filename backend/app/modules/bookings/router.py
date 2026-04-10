from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_booking_owner, require_roles

from .models import Booking
from .schemas import BookingCreate, BookingUpdate
from .service import (
    cancel_booking,
    create_booking,
    get_booking_by_id,
    list_bookings,
    update_booking,
)

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


def _require_user_id(user_id: str | None):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.get("", response_model=List[dict])
def get_bookings(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    _require_user_id(current_user.id)
    return list_bookings(db, current_user.id, skip=skip, limit=limit)


@router.get("/{booking_id}", response_model=dict)
def get_booking(
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    return get_booking_by_id(db, booking.id, booking.user_id)




@router.post("", response_model=dict, status_code=201)
def create_booking_endpoint(
    booking_data: BookingCreate,
    current_user: User = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    _require_user_id(current_user.id)
    data = booking_data.model_dump(exclude_unset=True)
    return create_booking(db, data, current_user.id)


@router.put("/{booking_id}", response_model=dict)
def update_booking_endpoint(
    booking_data: BookingUpdate,
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    update_data = {
        key: value
        for key, value in booking_data.model_dump(exclude_unset=True).items()
        if value is not None
    }
    return update_booking(db, booking.id, update_data, booking.user_id)


@router.patch("/{booking_id}", status_code=204)
def cancel_booking_endpoint(
    booking: Booking = Depends(require_booking_owner),
    db: Session = Depends(get_db),
):
    cancel_booking(db, booking.id, booking.user_id)
    return None
