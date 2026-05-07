"""Business logic for booking operations."""

from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import UUID, Session, select

from app.modules.bookings.schemas import BookingCreate, BookingResponse
from app.modules.listings.models import Listing
from app.modules.services.models import Service
from .models import Booking, BookingStatus
from app.modules.itineraries.models import ItineraryItem, Itinerary
from app.modules.discounts.models import Discount
from app.modules.pricing.service import calculate_display_price


def list_bookings(db: Session, user_id: UUID) -> List[BookingResponse]:
    query = (
        select(
            Booking,
            Service.name.label("service_name"),
            Listing.title.label("listing_name"))
        .outerjoin(Service, Booking.service_id == Service.service_id)
        .outerjoin(Listing, Service.listing_id == Listing.id)
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
        .outerjoin(Listing, Service.listing_id == Listing.id)
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


def price_booking_from_itinerary_item(db: Session, itinerary_item_id: UUID, user_id: UUID) -> dict:
    # 1. Get ItineraryItem by ID
    itinerary_item = db.get(ItineraryItem, itinerary_item_id)
    if not itinerary_item:
        raise HTTPException(status_code=404, detail="Itinerary item not found")

    # 2. Get Itinerary via itinerary_id and verify ownership
    itinerary = db.get(Itinerary, itinerary_item.itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    if itinerary.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this itinerary")

    # 3. Get pricing via PricingService (base_price from listing)
    price_info = calculate_display_price(db, itinerary_item.listing_id)
    base_price = float(price_info.get("base_price", 0.0))
    service_fee_percent = float(price_info.get("service_fee_percent", 0.0))
    service_fee_amount = base_price * service_fee_percent
    display_price = base_price + service_fee_amount

    # 4. Look up discount if itinerary has applied_discount_id set
    discount_percent = 0.0
    discount_amount = 0.0
    discount = None
    if (getattr(itinerary, "applied_discount_id", None) is not None) or getattr(itinerary, "applied_discount_rel", None) is not None:
        discount = itinerary.applied_discount_rel
        if discount is None and getattr(itinerary, "applied_discount_id", None) is not None:
            discount = db.get(Discount, itinerary.applied_discount_id)
        if discount:
            discount_percent = float(getattr(discount, "discount_percent", 0.0))

    # 5. Calculate discount amount with optional max
    raw_discount = display_price * discount_percent
    max_discount_amount = float(getattr(discount, "max_discount_amount", None)) if 'discount' in locals() and getattr(discount, "max_discount_amount", None) is not None else None
    if max_discount_amount is not None:
        discount_amount = min(raw_discount, max_discount_amount)
    else:
        discount_amount = raw_discount

    final_price = display_price - discount_amount

    return {
        "base_price": base_price,
        "service_fee_percent": service_fee_percent,
        "service_fee_amount": service_fee_amount,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "display_price": display_price,
        "final_price": final_price,
    }


def price_booking_by_id(db: Session, booking_id: UUID, user_id: UUID) -> dict:
    # Retrieve booking to determine pricing path
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Get listing_id via service relationship
    listing_id = None
    if booking.service_id:
        service = db.get(Service, booking.service_id)
        if service:
            listing_id = service.listing_id

    # If tied to an itinerary item, use itinerary-based pricing
    if booking.itinerary_item_id is not None:
        return price_booking_from_itinerary_item(db, booking.itinerary_item_id, user_id)

    # Use stored base_price if available, otherwise recalculate
    if booking.base_price is not None:
        base_price = float(booking.base_price)
        # Recalculate fee amounts since they may not be stored
        price_info = calculate_display_price(db, listing_id, booking.service_id)
        service_fee_percent = float(price_info.get("service_fee_percent", 0.10))
        service_fee_amount = base_price * service_fee_percent
        display_price = base_price + service_fee_amount
    else:
        price_info = calculate_display_price(db, listing_id, booking.service_id)
        base_price = float(price_info.get("base_price", 0.0))
        service_fee_percent = float(price_info.get("service_fee_percent", 0.10))
        service_fee_amount = base_price * service_fee_percent
        display_price = base_price + service_fee_amount

    discount_percent = float(booking.discount_percent or 0.0)
    discount_amount = float(booking.discount_amount or 0.0)
    final_price = display_price - discount_amount

    return {
        "base_price": base_price,
        "service_fee_percent": service_fee_percent,
        "service_fee_amount": service_fee_amount,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "display_price": display_price,
        "final_price": final_price,
    }


def create_booking(db: Session, booking: BookingCreate, user_id: UUID) -> Booking:
    booking = Booking(**booking.model_dump())
    booking.user_id = user_id

    # Get listing_id via service relationship if service_id provided
    listing_id = None
    if booking.service_id:
        service = db.get(Service, booking.service_id)
        if service:
            listing_id = service.listing_id

    # If booking is tied to an itinerary item, calculate price accordingly
    price_breakdown: Optional[dict] = None
    if booking.itinerary_item_id is not None:
        price_breakdown = price_booking_from_itinerary_item(db, booking.itinerary_item_id, user_id)
        # Populate price fields on the Booking object
        booking.base_price = price_breakdown.get("base_price")
        booking.service_fee_percent = price_breakdown.get("service_fee_percent")
        booking.service_fee_amount = price_breakdown.get("service_fee_amount")
        booking.discount_percent = price_breakdown.get("discount_percent")
        booking.discount_amount = price_breakdown.get("discount_amount")
        booking.display_price = price_breakdown.get("display_price")
        booking.final_price = price_breakdown.get("final_price")
    else:
        # Standalone booking: price via PricingService with no discount
        price_breakdown = calculate_display_price(db, listing_id, booking.service_id)
        booking.base_price = price_breakdown.get("base_price")
        booking.service_fee_percent = price_breakdown.get("service_fee_percent")
        booking.service_fee_amount = price_breakdown.get("service_fee_amount")
        booking.discount_percent = 0
        booking.discount_amount = 0
        booking.display_price = price_breakdown.get("display_price")
        booking.final_price = price_breakdown.get("final_price")

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
