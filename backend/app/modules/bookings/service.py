"""Business logic for booking operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, col, select, update

from app.modules.availability.service import (
    get_available_slots as availability_get_available_slots,
    get_booked_count as availability_get_booked_count,
    is_available as availability_is_available,
)
from app.modules.bookings.schemas import BookingCreate, BookingResponse
from app.modules.businesses.models import BusinessType
from app.modules.discounts.models import Discount
from app.modules.itineraries.models import Itinerary, ItineraryItem
from app.modules.listings.models import Listing
from app.modules.pricing.service import calculate_display_price
from app.modules.services.models import Service, StatusTypes

import stripe

from .models import Booking, BookingStatus, PaymentEvent


def _is_hotel_service(db: Session, service: Service) -> bool:
    """Check if a service belongs to a hotel business type."""
    if not service.listing_id:
        return False
    listing = db.get(Listing, service.listing_id)
    if not listing or not listing.business_type:
        return False
    business_type = db.get(BusinessType, listing.business_type)
    if not business_type:
        return False
    return business_type.name.lower() == "hotel"


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
    amount_of_people: int,
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

    # Apply per-person pricing for non-hotel services
    if not _is_hotel_service(db, service):
        base_price = base_price * amount_of_people

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
        # Use stored amount_of_people if available, otherwise default to 1
        # (for existing bookings, base_price is already multiplied)
        people = getattr(booking, 'amount_of_people', None) or 1
        return price_booking_from_itinerary_item(db, booking.itinerary_item_id, user_id, service, people)

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

    # Capacity check - calculate total booked people vs service capacity
    if service.service_id is not None and service.capacity is not None:
        from app.modules.availability.service import get_booked_count
        booked_count = get_booked_count(
            db,
            service.service_id,
            booking.booking_from_time,
            booking.booking_to_time,
        )
        available_slots = service.capacity - booked_count
        if available_slots < (booking.amount_of_people or 1):
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Service is not available for the selected time. "
                    f"Requested {booking.amount_of_people or 1} slot(s), but only {available_slots} remain."
                ),
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
            booking.amount_of_people or 1,
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
    # Check if time fields are being changed
    new_from_time = update_data.get("booking_from_time", booking.booking_from_time)
    new_to_time = update_data.get("booking_to_time", booking.booking_to_time)
    time_changed = (
        new_from_time != booking.booking_from_time or
        new_to_time != booking.booking_to_time
    )

    if time_changed:
        _validate_booking_window(new_from_time, new_to_time)

        # Conflict check - only approved bookings block
        if booking.service_id is not None and check_booking_conflict(
            db, booking.service_id, new_from_time, new_to_time, exclude_booking_id=booking.id
        ):
            raise HTTPException(
                status_code=409,
                detail="Booking conflict: overlapping booking exists for service",
            )

        # Capacity check - count approved bookings overlapping with new time, excluding self
        if booking.service_id is not None and booking.service is not None:
            from sqlalchemy import func
            booked_count = db.exec(
                select(func.coalesce(func.sum(Booking.amount_of_people), 0))
                .where(Booking.service_id == booking.service_id)
                .where(Booking.status == BookingStatus.approved)
                .where(Booking.id != booking.id)
                .where(Booking.booking_from_time < new_to_time)
                .where(Booking.booking_to_time > new_from_time)
).scalar_one_or_none()

            if booking.service.capacity is not None:
                available = booking.service.capacity - int(booked_count)
                if available < (booking.amount_of_people or 1):
                    raise HTTPException(
                        status_code=409,
                        detail="Not enough capacity for requested time",
                    )
    else:
        _validate_booking_window(
            update_data.get("booking_from_time", booking.booking_from_time),
            update_data.get("booking_to_time", booking.booking_to_time),
        )

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


def create_payment_intent(db: Session, booking_id: UUID, user_id: UUID) -> dict:
    """
    Create a Stripe Payment Intent for a booking.

    Returns dict with client_secret on success.
    Raises HTTPException if booking not found, not owned by user, not pending,
    or final_price < 0.50.
    """
    import os

    # Retrieve booking
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Verify user owns the booking
    if booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to pay for this booking")

    # Verify booking is pending
    if booking.status != BookingStatus.pending:
        raise HTTPException(status_code=400, detail="Booking is not in pending status")

    # Verify final_price >= 0.50 (calculate if None)
    if booking.final_price is None:
        # Calculate final_price from components
        base = float(booking.base_price or 0)
        fee = float(booking.service_fee_amount or 0)
        discount = float(booking.discount_amount or 0)
        calculated_final = base + fee - discount
        if calculated_final < 0.50:
            raise HTTPException(status_code=400, detail="Booking final price must be at least $0.50")
        booking.final_price = calculated_final
        db.add(booking)
        db.commit()
    elif booking.final_price < 0.50:
        raise HTTPException(status_code=400, detail="Booking final price must be at least $0.50")

    # Get Stripe key
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    # Create Stripe Payment Intent
    stripe.api_key = stripe_secret_key
    amount_cents = int(booking.final_price * 100)

    payment_intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        metadata={"booking_id": str(booking_id)},
        automatic_payment_methods={"enabled": True},
    )

    # Store payment intent ID on booking
    booking.stripe_payment_intent_id = payment_intent.id
    db.add(booking)

    # Create PaymentEvent record
    payment_event = PaymentEvent(
        booking_id=booking_id,
        event_type="payment_intent.created",
        stripe_payment_intent_id=payment_intent.id,
        amount_cents=amount_cents,
    )
    db.add(payment_event)

    db.commit()
    db.refresh(booking)

    return {"client_secret": payment_intent.client_secret}


def delete_booking(db: Session, booking: Booking) -> None:
    """Delete a cancelled booking. Only cancelled bookings can be deleted."""
    if booking.status != BookingStatus.cancelled:
        raise HTTPException(
            status_code=400,
            detail="Only cancelled bookings can be deleted",
        )
    db.delete(booking)
    db.commit()


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


def check_booking_conflict(
    db: Session,
    service_id: UUID,
    from_time: datetime,
    to_time: datetime,
    exclude_booking_id: UUID | None = None,
) -> bool:
    """
    Check if there are any approved bookings that overlap with the requested time window.

    Only `approved` bookings block - `completed` does NOT block because the booking
    period has passed. `cancelled` and `pending` also do not block.

    Overlap formula: (booking_from_time < to_time) AND (booking_to_time > from_time)
    Back-to-back bookings (A ends at 11:00, B starts at 11:00) do NOT conflict.

    Returns True if conflict exists, False otherwise.
    """
    query = (
        select(Booking)
        .where(Booking.service_id == service_id)
        .where(Booking.status == BookingStatus.approved)
        .where(Booking.booking_from_time < to_time)
        .where(Booking.booking_to_time > from_time)
    )

    if exclude_booking_id is not None:
        query = query.where(Booking.id != exclude_booking_id)

    result = db.exec(query).first()
    return result is not None


def update_expired_bookings(db: Session) -> dict:
    """
    Update booking statuses based on booking_to_time expiration.

    - approved -> completed when booking_to_time < now()
    - pending -> cancelled when booking_to_time < now()
    - Uses bulk SQL UPDATE for efficiency (no Python loops)
    """
    now = datetime.utcnow()

    # Bulk update approved bookings to completed
    approved_result = db.exec(
        update(Booking)
        .where(Booking.status == BookingStatus.approved)
        .where(Booking.booking_to_time.isnot(None))
        .where(Booking.booking_to_time < now)
        .values(status=BookingStatus.completed)
    )
    approved_count = approved_result.rowcount

    # Bulk update pending bookings to cancelled
    pending_result = db.exec(
        update(Booking)
        .where(Booking.status == BookingStatus.pending)
        .where(Booking.booking_to_time.isnot(None))
        .where(Booking.booking_to_time < now)
        .values(status=BookingStatus.cancelled)
    )
    pending_count = pending_result.rowcount

    # Single commit for both bulk updates
    if approved_count or pending_count:
        db.commit()

    return {"completed": approved_count, "cancelled": pending_count}
