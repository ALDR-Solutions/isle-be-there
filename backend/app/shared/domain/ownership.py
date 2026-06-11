from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.bookings.models import Booking
from app.modules.businesses.models import Business
from app.modules.itineraries.models import Itinerary
from app.modules.listings.models import EmployeeListings, Listing
from app.modules.reviews.models import Review
from app.modules.services.models import Service
from app.modules.users.models import User

from .lookups import get_business_or_404, get_listing_or_404


def is_admin_user(user: User) -> bool:
    return str(user.user_type) == "admin"


def ensure_booking_owner(
    user: User,
    booking: Booking,
    detail: str = "Not authorized",
) -> Booking:
    if is_admin_user(user) or str(booking.user_id) == str(user.id):
        return booking
    raise HTTPException(status_code=403, detail=detail)


def ensure_review_owner(
    user: User,
    review: Review,
    detail: str = "Not authorized",
) -> Review:
    if is_admin_user(user) or str(review.user_id) == str(user.id):
        return review
    raise HTTPException(status_code=403, detail=detail)


def ensure_business_owner(
    user: User,
    business: Business,
    detail: str = "Not authorized",
) -> Business:
    if is_admin_user(user) or str(business.user_id) == str(user.id):
        return business
    raise HTTPException(status_code=403, detail=detail)


def ensure_listing_belongs_to_business(
    listing: Listing,
    business: Business,
    detail: str = "Listing does not belong to this business",
) -> Listing:
    if str(listing.business_id) != str(business.id):
        raise HTTPException(status_code=403, detail=detail)
    return listing


def ensure_listing_owner(
    db: Session,
    user: User,
    listing: Listing,
    detail: str = "Not authorized",
) -> Listing:
    if is_admin_user(user):
        return listing
    if not listing.business_id:
        raise HTTPException(status_code=403, detail=detail)

    business = get_business_or_404(db, listing.business_id)
    ensure_business_owner(user, business, detail=detail)
    return listing


def ensure_itinerary_owner(
    itinerary: Itinerary,
    user_id: UUID | str,
    detail: str = "Not authorized for this itinerary",
) -> Itinerary:
    if str(itinerary.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail=detail)
    return itinerary


def ensure_service_access(
    db: Session,
    user: User,
    service: Service,
    detail: str = "Not authorized",
) -> Service:
    if is_admin_user(user):
        return service

    listing = get_listing_or_404(db, service.listing_id)

    if listing.business_id:
        business = get_business_or_404(db, listing.business_id)
        if str(business.user_id) == str(user.id):
            return service

    assignment = db.exec(
        select(EmployeeListings).where(
            EmployeeListings.listing_id == listing.id,
            EmployeeListings.employee_id == user.id,
        )
    ).first()
    if assignment:
        return service

    raise HTTPException(status_code=403, detail=detail)


def ensure_listing_service_manager(
    db: Session,
    user: User,
    listing: Listing,
    detail: str = "Not authorized",
) -> Listing:
    if is_admin_user(user):
        return listing

    if listing.business_id:
        business = get_business_or_404(db, listing.business_id)
        if str(business.user_id) == str(user.id):
            return listing

    assignment = db.exec(
        select(EmployeeListings).where(
            EmployeeListings.listing_id == listing.id,
            EmployeeListings.employee_id == user.id,
        )
    ).first()
    if assignment:
        return listing

    raise HTTPException(status_code=403, detail=detail)
