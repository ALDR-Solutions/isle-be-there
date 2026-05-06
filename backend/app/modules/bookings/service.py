"""Business logic for booking operations."""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, col, func, select

from .models import Booking, BookingStatus


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
    
def get_booked_count(
    db: Session,
    service_id: UUID,
    start_dt: datetime,
    end_dt: datetime,
) -> int:
    """Count confirmed bookings that overlap the requested window."""
    result = db.exec(
        select(func.coalesce(func.sum(Booking.amount_of_people), 0))
        .where(Booking.service_id == service_id)
        .where(col(Booking.status).notin_([
            BookingStatus.cancelled,
            BookingStatus.pending,
        ]))
        # Overlap condition: existing booking starts before our end
        # AND ends after our start
        .where(Booking.booking_from_time < end_dt)
        .where(Booking.booking_to_time > start_dt)
    ).one()
    return int(result or 0)


def get_available_slots(
    db: Session,
    service_id: UUID,
    capacity: int,
    start_dt: datetime,
    end_dt: datetime,
) -> int:
    booked = get_booked_count(db, service_id, start_dt, end_dt)
    return max(0, capacity - booked)


def is_available(
    db: Session,
    service_id: UUID,
    capacity: int,
    start_dt: datetime,
    end_dt: datetime,
    requested_quantity: int = 1,
) -> bool:
    return get_available_slots(db, service_id, capacity, start_dt, end_dt) >= requested_quantity
