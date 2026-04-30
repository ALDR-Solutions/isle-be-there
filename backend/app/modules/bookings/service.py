"""Business logic for booking operations."""

from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import UUID, Session, select

from app.modules.bookings.schemas import BookingCreate, BookingResponse
from app.modules.listings.models import Listing
from app.modules.services.models import Service
from .models import Booking, BookingStatus


def list_bookings(db: Session, user_id: UUID) -> List[BookingResponse]:
    query = (
        select(
            Booking, 
            Service.name.label("service_name"),
            Listing.title.label("listing_name"))
        .outerjoin(Service, Booking.service_id == Service.service_id)
        .outerjoin(Listing, Booking.listing_id == Listing.id)
        .where(Booking.user_id == user_id)
    )
    results = db.exec(query).all()

    if not results:
        raise HTTPException(status_code=404, detail="Bookings not found")
    

    return [
        BookingResponse(
            **booking.model_dump(),
            service_name=service_name,
            listing_name=listing_name,
        )
        for booking, service_name, listing_name in results
    ]


def get_booking_by_id(db: Session, booking_id: UUID, user_id: UUID) -> BookingResponse:
    query = (
        select(
            Booking,
            Service.name.label("service_name"),
            Listing.title.label("listing_name")
        )
        .outerjoin(Service, Booking.service_id == Service.service_id)
        .outerjoin(Listing, Booking.listing_id == Listing.id)
        .where(
            Booking.id == booking_id,
            Booking.user_id == user_id
        )
    )

    result = db.exec(query).first()

    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking, service_name, listing_name = result

    return BookingResponse(
        **booking.model_dump(),
        service_name=service_name,
        listing_name=listing_name,
    )


def create_booking(db: Session, booking: BookingCreate, user_id: UUID) -> Booking:
    booking = Booking(**booking.model_dump())
    booking.user_id = user_id

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def update_booking(db: Session, booking: Booking, update_data: dict) -> Booking:

    for key, value in update_data.items():
        setattr(booking, key, value)

    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, booking: Booking) -> Booking:
    booking.status = BookingStatus.cancelled

    db.commit()
    db.refresh(booking)
    return booking
