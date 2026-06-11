from __future__ import annotations

from typing import TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.bookings.models import Booking
from app.modules.businesses.models import Business
from app.modules.itineraries.models import Itinerary, ItineraryItem
from app.modules.listings.models import Listing
from app.modules.reviews.models import Review
from app.modules.services.models import Service
from app.modules.users.models import User

T = TypeVar("T")


def raise_not_found(detail: str) -> None:
    raise HTTPException(status_code=404, detail=detail)


def get_or_404(entity: T | None, detail: str) -> T:
    if entity is None:
        raise_not_found(detail)
    return entity


def get_user_by_id(db: Session, user_id: UUID | str) -> User | None:
    return db.get(User, user_id)


def get_user_or_404(
    db: Session,
    user_id: UUID | str,
    detail: str = "User not found",
) -> User:
    return get_or_404(get_user_by_id(db, user_id), detail)


def get_business_by_user_id(db: Session, user_id: UUID | str) -> Business | None:
    return db.exec(select(Business).where(Business.user_id == user_id)).first()


def get_business_or_404(
    db: Session,
    business_id: UUID | str,
    detail: str = "Business not found",
) -> Business:
    return get_or_404(db.get(Business, business_id), detail)


def get_listing_or_404(
    db: Session,
    listing_id: UUID | str,
    detail: str = "Listing not found",
) -> Listing:
    return get_or_404(db.get(Listing, listing_id), detail)


def get_service_or_404(
    db: Session,
    service_id: UUID | str,
    detail: str = "Service not found",
) -> Service:
    return get_or_404(db.get(Service, service_id), detail)


def get_booking_or_404(
    db: Session,
    booking_id: UUID | str,
    detail: str = "Booking not found",
) -> Booking:
    return get_or_404(db.get(Booking, booking_id), detail)


def get_review_or_404(
    db: Session,
    review_id,
    detail: str = "Review not found",
) -> Review:
    return get_or_404(db.get(Review, review_id), detail)


def get_itinerary_or_404(
    db: Session,
    itinerary_id: UUID | str,
    detail: str = "Itinerary not found",
) -> Itinerary:
    return get_or_404(db.get(Itinerary, itinerary_id), detail)


def get_itinerary_item_or_404(
    db: Session,
    itinerary_item_id: UUID | str,
    detail: str = "Itinerary item not found",
) -> ItineraryItem:
    return get_or_404(db.get(ItineraryItem, itinerary_item_id), detail)
