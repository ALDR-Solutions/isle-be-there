from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user_id
from app.database import get_db
from app.schemas.booking import BookingCreate, BookingUpdate
from app.services.booking_service import (
    list_bookings,
    get_booking_by_id,
    create_booking,
    update_booking,
    cancel_booking,
)

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


def _require_user_id(user_id: str | None):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.get("", response_model=List[dict])
def get_bookings(
    skip: int = 0,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    return list_bookings(db, user_id, skip=skip, limit=limit)


@router.get("/{booking_id}", response_model=dict)
def get_booking(
    booking_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    return get_booking_by_id(db, booking_id, user_id)


@router.post("", response_model=dict, status_code=201)
def create_booking_endpoint(
    booking_data: BookingCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    data = booking_data.dict(exclude_unset=True)
    return create_booking(db, data, user_id)


@router.put("/{booking_id}", response_model=dict)
def update_booking_endpoint(
    booking_id: int,
    booking_data: BookingUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    update_data = {k: v for k, v in booking_data.dict(exclude_unset=True).items() if v is not None}
    return update_booking(db, booking_id, update_data, user_id)


@router.delete("/{booking_id}", status_code=204)
def cancel_booking_endpoint(
    booking_id: int,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    cancel_booking(db, booking_id, user_id)
    return None
