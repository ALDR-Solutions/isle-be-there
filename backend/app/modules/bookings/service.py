"""Business logic for booking operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, col, select

from app.modules.availability.service import (
    get_available_slots as availability_get_available_slots,
    get_booked_count as availability_get_booked_count,
    is_available as availability_is_available,
)
from app.modules.bookings.schemas import BookingCreate, BookingResponse
from app.modules.discounts.models import Discount
from app.modules.itineraries.models import Itinerary, ItineraryItem
from app.modules.listings.models import Listing
from app.modules.pricing.service import calculate_display_price
from app.modules.services.models import Service, StatusTypes

from .models import Booking, BookingStatus


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


def _get_service_or_404(db: Session, service_id: UUID) -> Service:
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


def _validate_booking_window(booking_from_time: Optional[datetime], booking_to_time: Optional[datetime]) -> None:
    if booking_from_time is None or booking_to_time is None:
        raise HTTPException(status_code=400, detail="Booking start and end time are required")
    if booking_to_time <= booking_from_time:
        raise HTTPException(status_code=400, detail="Booking end time must be after start time")


def _validate_service_for_booking(
    db: Session,
    service_id: UUID,
    itinerary_item_id: Optional[UUID],
    user_id: UUID,
) -> tuple[Service, Optional[ItineraryItem]]:
    service = _get_service_or_404(db, service_id)
    if service.status != StatusTypes.active:
        raise HTTPException(status_code=400, detail="Only active services can be booked")

    itinerary_item = None
    if itinerary_item_id is not None:
        itinerary_item = db.get(ItineraryItem, itinerary_item_id)
        if not itinerary_item:
            raise HTTPException(status_code=404, detail="Itinerary item not found")

        itinerary = db.get(Itinerary, itinerary_item.itinerary_id)
        if not itinerary:
            raise HTTPException(status_code=404, detail="Itinerary not found")
        if itinerary.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized for this itinerary")
        if service.listing_id != itinerary_item.listing_id:
            raise HTTPException(
                status_code=400,
                detail="Selected service does not belong to this itinerary item's listing",
            )

    return service, itinerary_item


def _validate_service_capacity(
    db: Session,
    service: Service,
    booking_from_time: datetime,
    booking_to_time: datetime,
    amount_of_people: int,
) -> None:
    if service.capacity is None:
        return
    if amount_of_people < 1:
        raise HTTPException(status_code=400, detail="Amount of people must be at least 1")
    available_slots = get_available_slots(
        db,
        service.service_id,
        service.capacity,
        booking_from_time,
        booking_to_time,
    )
    if available_slots < amount_of_people:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Service is not available for the selected time. "
                f"Requested {amount_of_people} slot(s), but only {available_slots} remain."
            ),
        )


def price_booking_from_itinerary_item(
    db: Session,
    itinerary_item_id: UUID,
    user_id: UUID,
    service: Service,
) -> dict:
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

    # 3. Get pricing via PricingService using the selected service
    price_info = calculate_display_price(db, service.listing_id, service.service_id)
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

    if booking.service_id is None:
        raise HTTPException(status_code=400, detail="Booking is missing a linked service")

    service = _get_service_or_404(db, booking.service_id)
    listing_id = service.listing_id

    # If tied to an itinerary item, use itinerary-based pricing
    if booking.itinerary_item_id is not None:
        return price_booking_from_itinerary_item(db, booking.itinerary_item_id, user_id, service)

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
    _validate_booking_window(booking.booking_from_time, booking.booking_to_time)
    service, _ = _validate_service_for_booking(
        db,
        booking.service_id,
        booking.itinerary_item_id,
        user_id,
    )
    _validate_service_capacity(
        db,
        service,
        booking.booking_from_time,
        booking.booking_to_time,
        booking.amount_of_people or 1,
    )

    booking_record = Booking(**booking.model_dump())
    booking_record.user_id = user_id

    # If booking is tied to an itinerary item, calculate price accordingly
    price_breakdown: Optional[dict] = None
    if booking_record.itinerary_item_id is not None:
        price_breakdown = price_booking_from_itinerary_item(
            db,
            booking_record.itinerary_item_id,
            user_id,
            service,
        )
        # Populate price fields on the Booking object
        booking_record.base_price = price_breakdown.get("base_price")
        booking_record.service_fee_percent = price_breakdown.get("service_fee_percent")
        booking_record.service_fee_amount = price_breakdown.get("service_fee_amount")
        booking_record.discount_percent = price_breakdown.get("discount_percent")
        booking_record.discount_amount = price_breakdown.get("discount_amount")
        booking_record.display_price = price_breakdown.get("display_price")
        booking_record.final_price = price_breakdown.get("final_price")
    else:
        # Standalone booking: price via PricingService with no discount
        price_breakdown = calculate_display_price(db, service.listing_id, service.service_id)
        booking_record.base_price = price_breakdown.get("base_price")
        booking_record.service_fee_percent = price_breakdown.get("service_fee_percent")
        booking_record.service_fee_amount = price_breakdown.get("service_fee_amount")
        booking_record.discount_percent = 0
        booking_record.discount_amount = 0
        booking_record.display_price = price_breakdown.get("display_price")
        booking_record.final_price = price_breakdown.get("final_price")

    db.add(booking_record)
    db.commit()
    db.refresh(booking_record)
    return booking_record


def create_bulk_bookings(db: Session, items: List[BookingCreate], user_id: UUID) -> List[Booking]:
    """Create multiple bookings atomically. All succeed or all fail."""
    bookings = []
    try:
        for booking_data in items:
            booking = create_booking(db, booking_data, user_id)
            bookings.append(booking)
        return bookings
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Bulk booking failed: {str(e)}")


def update_booking(db: Session, booking: Booking, update_data: dict) -> Booking:
    next_from_time = update_data.get("booking_from_time", booking.booking_from_time)
    next_to_time = update_data.get("booking_to_time", booking.booking_to_time)
    _validate_booking_window(next_from_time, next_to_time)

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
    
def get_booked_count(
    db: Session,
    service_id: UUID,
    start_dt: datetime,
    end_dt: datetime,
) -> int:
    """Count confirmed bookings that overlap the requested window."""
    return availability_get_booked_count(db, service_id, start_dt, end_dt)


def get_available_slots(
    db: Session,
    service_id: UUID,
    capacity: int,
    start_dt: datetime,
    end_dt: datetime,
) -> int:
    """Calculate available slots (capacity minus booked)."""
    return availability_get_available_slots(db, service_id, capacity, start_dt, end_dt)


def is_available(
    db: Session,
    service_id: UUID,
    capacity: int,
    start_dt: datetime,
    end_dt: datetime,
    requested_quantity: int = 1,
) -> bool:
    """Check if service is available for requested quantity."""
    return availability_is_available(db, service_id, capacity, start_dt, end_dt, requested_quantity)
