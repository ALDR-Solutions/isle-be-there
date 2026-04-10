"""Business logic for booking operations."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.listings.models import Listing
from app.modules.services.models import Service
from app.modules.services.service import get_service_by_id
from .models import Booking


def list_bookings(db: Session, user_id: str, skip: int = 0, limit: int = 20):
    bookings = db.exec(select(Booking).where(Booking.user_id == user_id).offset(skip).limit(limit)).all()
    return [booking.model_dump() for booking in bookings]


def get_booking_by_id(db: Session, booking_id: int, user_id: str):
    booking = db.exec(select(Booking).where(Booking.id == booking_id)).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if str(booking.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return booking.model_dump()




def create_booking(db: Session, booking_data: dict, user_id: str):
    booking = Booking(**booking_data)
    booking.user_id = user_id

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking.model_dump()


def update_booking(db: Session, booking_id: int, update_data: dict, user_id: str):
    booking = db.exec(select(Booking).where(Booking.id == booking_id)).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if str(booking.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in update_data.items():
        setattr(booking, key, value)
    db.commit()
    db.refresh(booking)
    return booking.model_dump()


def cancel_booking(db: Session, booking_id: int, user_id: str):
    booking = db.exec(select(Booking).where(Booking.id == booking_id)).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if str(booking.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
