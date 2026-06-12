"""Business logic for booking operations."""

from dataclasses import dataclass, field
from datetime import datetime
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, col, select, update

from app.modules.availability.service import (
    get_available_slots as availability_get_available_slots,
    get_booked_count as availability_get_booked_count,
    get_service_slot_for_service,
    is_available as availability_is_available,
)
from app.modules.availability.models import ServiceSlots
from app.modules.bookings.schemas import BookingCreate, BookingResponse
from app.modules.businesses.models import BusinessType
from app.modules.discounts.service import (
    calculate_discount_for_amount,
    get_eligible_package_discount,
    normalize_fractional_percent as normalize_discount_percent,
)
from app.modules.itineraries.models import Itinerary, ItineraryItem
from app.modules.listings.models import Listing
from app.modules.pricing.models import PlatformPricingConfig
from app.modules.pricing.service import (
    calculate_display_price,
    normalize_fractional_percent as normalize_pricing_percent,
    query_active_config,
)
from app.modules.services.models import Service, StatusTypes
from app.modules.stripe_payment.models import PaymentEvent
from app.shared.domain import (
    get_owned_itinerary_item_context_or_404,
    get_service_or_404,
)
from .models import Booking, BookingStatus

logger = logging.getLogger(__name__)


@dataclass
class BookingCreationContext:
    services: dict[UUID, Service] = field(default_factory=dict)
    listings: dict[UUID, Listing | None] = field(default_factory=dict)
    business_types: dict[UUID, BusinessType | None] = field(default_factory=dict)
    itinerary_items: dict[UUID, ItineraryItem] = field(default_factory=dict)
    itineraries: dict[UUID, Itinerary] = field(default_factory=dict)
    display_prices: dict[tuple[UUID, UUID | None], dict] = field(default_factory=dict)
    pricing_configs: dict[UUID | None, PlatformPricingConfig | None] = field(
        default_factory=dict
    )
    package_discounts: dict[UUID, object | None] = field(default_factory=dict)
    slot_selection_required: dict[tuple[UUID, int], bool] = field(default_factory=dict)


def get_service_for_booking_or_404(
    db: Session,
    service_id: UUID,
    *,
    context: BookingCreationContext | None = None,
) -> Service:
    if context is not None and service_id in context.services:
        return context.services[service_id]

    service = get_service_or_404(db, service_id)
    if context is not None:
        context.services[service_id] = service
    return service


def get_listing_for_booking(
    db: Session,
    listing_id: UUID | None,
    *,
    context: BookingCreationContext | None = None,
) -> Listing | None:
    if listing_id is None:
        return None
    if context is not None and listing_id in context.listings:
        return context.listings[listing_id]

    listing = db.get(Listing, listing_id)
    if context is not None:
        context.listings[listing_id] = listing
    return listing


def get_business_type_for_booking(
    db: Session,
    business_type_id: UUID | None,
    *,
    context: BookingCreationContext | None = None,
) -> BusinessType | None:
    if business_type_id is None:
        return None
    if context is not None and business_type_id in context.business_types:
        return context.business_types[business_type_id]

    business_type = db.get(BusinessType, business_type_id)
    if context is not None:
        context.business_types[business_type_id] = business_type
    return business_type


def get_owned_itinerary_item_context_cached_or_404(
    db: Session,
    itinerary_item_id: UUID,
    user_id: UUID,
    *,
    context: BookingCreationContext | None = None,
) -> tuple[ItineraryItem, Itinerary]:
    if context is not None and itinerary_item_id in context.itinerary_items:
        itinerary_item = context.itinerary_items[itinerary_item_id]
        itinerary = context.itineraries.get(itinerary_item.itinerary_id)
        if itinerary is None or str(itinerary.user_id) != str(user_id):
            raise HTTPException(status_code=404, detail="Itinerary not found")
        return itinerary_item, itinerary

    return get_owned_itinerary_item_context_or_404(db, itinerary_item_id, user_id)


def get_service_business_type_name(
    db: Session,
    service: Service,
    *,
    context: BookingCreationContext | None = None,
) -> str | None:
    if not service.listing_id:
        return None

    listing = get_listing_for_booking(db, service.listing_id, context=context)
    if not listing or not listing.business_type:
        return None

    business_type = get_business_type_for_booking(
        db,
        listing.business_type,
        context=context,
    )
    if not business_type or not business_type.name:
        return None

    return business_type.name.lower()


def is_hotel_service(
    db: Session,
    service: Service,
    *,
    context: BookingCreationContext | None = None,
) -> bool:
    """Check if a service belongs to a hotel business type."""
    return get_service_business_type_name(db, service, context=context) == "hotel"


def is_restaurant_service(
    db: Session,
    service: Service,
    *,
    context: BookingCreationContext | None = None,
) -> bool:
    """Check if a service belongs to a restaurant business type."""
    return get_service_business_type_name(db, service, context=context) == "restaurant"


def get_pricing_config_cached(
    db: Session,
    business_type_id: UUID | None,
    *,
    context: BookingCreationContext | None = None,
) -> PlatformPricingConfig | None:
    if context is None:
        return query_active_config(db, business_type_id)

    if business_type_id not in context.pricing_configs:
        context.pricing_configs[business_type_id] = query_active_config(
            db,
            business_type_id,
        )
    return context.pricing_configs[business_type_id]


def calculate_display_price_for_booking(
    db: Session,
    listing_id: UUID,
    service_id: UUID | None = None,
    *,
    context: BookingCreationContext | None = None,
) -> dict:
    if context is None:
        return calculate_display_price(db, listing_id, service_id)

    cache_key = (listing_id, service_id)
    if cache_key in context.display_prices:
        return context.display_prices[cache_key]

    listing = get_listing_for_booking(db, listing_id, context=context)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    base_price = None
    if service_id is not None:
        service = get_service_for_booking_or_404(db, service_id, context=context)
        if getattr(service, "price", None) is not None:
            base_price = service.price
    if base_price is None:
        base_price = listing.base_price
    if base_price is None:
        raise HTTPException(status_code=400, detail="Listing has no base price set")

    config = None
    if getattr(listing, "business_type", None) is not None:
        config = get_pricing_config_cached(
            db,
            listing.business_type,
            context=context,
        )
    if config is None:
        config = get_pricing_config_cached(db, None, context=context)

    service_fee_percent = getattr(config, "service_fee_percent", None) if config else 0.10
    if service_fee_percent is None:
        service_fee_percent = 0.10
    service_fee_percent = normalize_pricing_percent(service_fee_percent)
    service_fee_amount = float(base_price) * float(service_fee_percent)
    display_price = float(base_price) + service_fee_amount

    result = {
        "base_price": base_price,
        "service_fee_percent": float(service_fee_percent),
        "service_fee_amount": service_fee_amount,
        "display_price": display_price,
    }
    context.display_prices[cache_key] = result
    return result


def get_eligible_package_discount_cached(
    db: Session,
    itinerary: Itinerary,
    *,
    context: BookingCreationContext | None = None,
):
    if context is None:
        return get_eligible_package_discount(db, itinerary)

    if itinerary.id not in context.package_discounts:
        context.package_discounts[itinerary.id] = get_eligible_package_discount(
            db,
            itinerary,
        )
    return context.package_discounts[itinerary.id]


def build_booking_creation_context(
    db: Session,
    items: List[BookingCreate],
) -> BookingCreationContext:
    context = BookingCreationContext()

    service_ids = list({item.service_id for item in items if item.service_id})
    if service_ids:
        services = db.exec(
            select(Service).where(Service.service_id.in_(service_ids))
        ).all()
        context.services = {service.service_id: service for service in services}

        listing_ids = list(
            {
                service.listing_id
                for service in services
                if getattr(service, "listing_id", None) is not None
            }
        )
        if listing_ids:
            listings = db.exec(select(Listing).where(Listing.id.in_(listing_ids))).all()
            context.listings = {listing.id: listing for listing in listings}

            business_type_ids = list(
                {
                    listing.business_type
                    for listing in listings
                    if getattr(listing, "business_type", None) is not None
                }
            )
            if business_type_ids:
                business_types = db.exec(
                    select(BusinessType).where(BusinessType.id.in_(business_type_ids))
                ).all()
                context.business_types = {
                    business_type.id: business_type for business_type in business_types
                }

    itinerary_item_ids = list(
        {item.itinerary_item_id for item in items if item.itinerary_item_id is not None}
    )
    if itinerary_item_ids:
        itinerary_items = db.exec(
            select(ItineraryItem).where(ItineraryItem.id.in_(itinerary_item_ids))
        ).all()
        context.itinerary_items = {
            itinerary_item.id: itinerary_item for itinerary_item in itinerary_items
        }

        itinerary_ids = list(
            {item.itinerary_id for item in itinerary_items if item.itinerary_id is not None}
        )
        if itinerary_ids:
            itineraries = db.exec(
                select(Itinerary).where(Itinerary.id.in_(itinerary_ids))
            ).all()
            context.itineraries = {itinerary.id: itinerary for itinerary in itineraries}

    return context


def booking_summary_query():
    confirmed_payment_events = (
        select(
            PaymentEvent.booking_id.label("booking_id"),
            func.max(PaymentEvent.created_at).label("paid_at"),
        )
        .where(PaymentEvent.event_type == "payment_intent.confirmed")
        .group_by(PaymentEvent.booking_id)
        .subquery()
    )
    refund_events = (
        select(
            PaymentEvent.booking_id.label("booking_id"),
            func.min(PaymentEvent.created_at).label("refund_date"),
        )
        .where(PaymentEvent.event_type.like("refund.%"))
        .group_by(PaymentEvent.booking_id)
        .subquery()
    )
    return (
        select(
            Booking,
            Service.name.label("service_name"),
            Listing.title.label("listing_name"),
            BusinessType.name.label("listing_business_type_name"),
            confirmed_payment_events.c.paid_at.label("paid_at"),
            refund_events.c.refund_date.label("refund_date"),
            ItineraryItem.itinerary_id.label("itinerary_id"),
        )
        .outerjoin(Service, Booking.service_id == Service.service_id)
        .outerjoin(Listing, Service.listing_id == Listing.id)
        .outerjoin(BusinessType, Listing.business_type == BusinessType.id)
        .outerjoin(
            confirmed_payment_events,
            confirmed_payment_events.c.booking_id == Booking.id,
        )
        .outerjoin(
            refund_events,
            refund_events.c.booking_id == Booking.id,
        )
        .outerjoin(
            ItineraryItem,
            Booking.itinerary_item_id == ItineraryItem.id,
        )
    )


def build_booking_response(
    booking: Booking,
    service_name: Optional[str],
    listing_name: Optional[str],
    listing_business_type_name: Optional[str],
    paid_at: Optional[datetime],
    refund_date: Optional[datetime],
    itinerary_id: Optional[UUID] = None,
) -> BookingResponse:
    return BookingResponse(
        **booking.model_dump(),
        service_name=service_name,
        listing_name=listing_name,
        listing_business_type_name=listing_business_type_name,
        paid_at=paid_at,
        has_refund=refund_date is not None,
        refund_date=refund_date,
        itinerary_id=itinerary_id,
    )


def list_bookings(db: Session, user_id: UUID) -> List[BookingResponse]:
    query = booking_summary_query().where(Booking.user_id == user_id)
    results = db.exec(query).all()

    return [
        build_booking_response(
            booking,
            service_name,
            listing_name,
            listing_business_type_name,
            paid_at,
            refund_date,
            itinerary_id,
        )
        for (
            booking,
            service_name,
            listing_name,
            listing_business_type_name,
            paid_at,
            refund_date,
            itinerary_id,
        ) in results
    ]


def booking_has_refund(db: Session, booking_id: UUID) -> bool:
    """Check if booking has any refund.* PaymentEvent."""
    refund_event = db.exec(
        select(PaymentEvent).where(
            PaymentEvent.booking_id == booking_id,
            PaymentEvent.event_type.like("refund.%"),
        )
    ).first()
    return refund_event is not None


def get_booking_by_id(db: Session, booking_id: UUID, user_id: UUID) -> BookingResponse:
    query = booking_summary_query().where(
        Booking.id == booking_id,
        Booking.user_id == user_id,
    )

    result = db.exec(query).first()

    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")

    (
        booking,
        service_name,
        listing_name,
        listing_business_type_name,
        paid_at,
        refund_date,
        itinerary_id,
    ) = result

    # Recalculate price to ensure it reflects current people count and stay duration
    # This is important for displaying accurate prices on the booking details page
    if booking.service_id is not None:
        try:
            recalculated = price_booking_by_id(db, booking_id, user_id)
            # Update booking fields with recalculated prices
            booking.base_price = recalculated["base_price"]
            booking.service_fee_percent = recalculated["service_fee_percent"]
            booking.service_fee_amount = recalculated["service_fee_amount"]
            booking.discount_percent = recalculated["discount_percent"]
            booking.discount_amount = recalculated["discount_amount"]
            booking.display_price = recalculated["display_price"]
            booking.final_price = recalculated["final_price"]
        except Exception:
            # If recalculation fails, use stored prices (booking might be old)
            pass

    return build_booking_response(
        booking,
        service_name,
        listing_name,
        listing_business_type_name,
        paid_at,
        refund_date,
        itinerary_id,
    )


def list_bookings_for_listing(db: Session, listing_id: UUID) -> List[BookingResponse]:
    query = booking_summary_query().where(Service.listing_id == listing_id)
    results = db.exec(query).all()

    return [
        build_booking_response(
            booking,
            service_name,
            listing_name,
            listing_business_type_name,
            paid_at,
            refund_date,
            itinerary_id,
        )
        for (
            booking,
            service_name,
            listing_name,
            listing_business_type_name,
            paid_at,
            refund_date,
            itinerary_id,
        ) in results
    ]


def get_refund_date(db: Session, booking_id: UUID) -> Optional[datetime]:
    """Get the date of the first refund.* PaymentEvent for a booking."""
    refund_event = db.exec(
        select(PaymentEvent)
        .where(
            PaymentEvent.booking_id == booking_id,
            PaymentEvent.event_type.like("refund.%"),
        )
        .order_by(PaymentEvent.created_at)
    ).first()
    return refund_event.created_at if refund_event else None


def validate_booking_window(
    booking_from_time: Optional[datetime], booking_to_time: Optional[datetime]
) -> None:
    if booking_from_time is None or booking_to_time is None:
        raise HTTPException(
            status_code=400, detail="Booking start and end time are required"
        )
    if booking_to_time <= booking_from_time:
        raise HTTPException(
            status_code=400, detail="Booking end time must be after start time"
        )


def get_booking_day_of_week(booking_time: datetime) -> int:
    """Convert Python weekday() (Mon=0) to DB weekday (Sun=0)."""
    return (booking_time.weekday() + 1) % 7


def booking_requires_slot_selection(
    db: Session,
    service_id: UUID,
    booking_from_time: Optional[datetime],
    *,
    context: BookingCreationContext | None = None,
) -> bool:
    if booking_from_time is None:
        return False

    day_of_week = get_booking_day_of_week(booking_from_time)
    cache_key = (service_id, day_of_week)
    if context is not None and cache_key in context.slot_selection_required:
        return context.slot_selection_required[cache_key]

    service = get_service_for_booking_or_404(db, service_id, context=context)
    if service and is_hotel_service(db, service, context=context):
        if context is not None:
            context.slot_selection_required[cache_key] = False
        return False

    slot = db.exec(
        select(ServiceSlots.id)
        .where(ServiceSlots.service_id == service_id)
        .where(ServiceSlots.day_of_week == day_of_week)
    ).first()
    requires_slot = slot is not None
    if context is not None:
        context.slot_selection_required[cache_key] = requires_slot
    return requires_slot


def resolve_booking_slot_context(
    db: Session,
    service_id: UUID,
    service_slot_id: int,
    booking_from_time: Optional[datetime],
    booking_to_time: Optional[datetime],
    *,
    context: BookingCreationContext | None = None,
) -> tuple[ServiceSlots | None, datetime, datetime]:
    booking_date_source = booking_from_time or booking_to_time
    if booking_date_source is None:
        raise HTTPException(
            status_code=400,
            detail="Booking date is required when selecting a service slot",
        )

    booking_day_of_week = get_booking_day_of_week(booking_date_source)

    # Handle virtual slot (id=-1) from listing hours fallback
    if service_slot_id == -1:
        service = get_service_for_booking_or_404(db, service_id, context=context)
        if not service.listing_id:
            raise HTTPException(
                status_code=400, detail="Service has no listing associated"
            )

        from app.modules.availability.service import get_listing_hours

        listing_hours = get_listing_hours(db, service.listing_id, booking_day_of_week)
        if not listing_hours:
            raise HTTPException(
                status_code=400,
                detail="No listing hours found for the selected date - cannot use virtual slot",
            )

        slot_start = datetime.combine(
            booking_date_source.date(), listing_hours.open_time
        )
        slot_end = datetime.combine(
            booking_date_source.date(), listing_hours.close_time
        )
        # Return None for slot since it's a virtual slot (no actual ServiceSlots record)
        return None, slot_start, slot_end

    slot = get_service_slot_for_service(db, service_id, service_slot_id)
    if slot is None:
        raise HTTPException(
            status_code=400, detail="Selected service slot is invalid for this service"
        )

    if booking_day_of_week != slot.day_of_week:
        raise HTTPException(
            status_code=400,
            detail="Selected service slot does not match the chosen booking date",
        )

    slot_start = datetime.combine(booking_date_source.date(), slot.start_time)
    slot_end = datetime.combine(booking_date_source.date(), slot.end_time)
    return slot, slot_start, slot_end


def validate_slot_capacity(
    db: Session,
    slot: ServiceSlots,
    booking_from_time: datetime,
    booking_to_time: datetime,
    amount_of_people: int,
    *,
    exclude_booking_id: UUID | None = None,
) -> None:
    if amount_of_people < 1:
        raise HTTPException(
            status_code=400, detail="Amount of people must be at least 1"
        )

    booked_count_query = (
        select(func.coalesce(func.sum(Booking.amount_of_people), 0))
        .where(Booking.service_id == slot.service_id)
        .where(
            col(Booking.status).notin_([BookingStatus.cancelled, BookingStatus.pending])
        )
        .where(Booking.booking_from_time < booking_to_time)
        .where(Booking.booking_to_time > booking_from_time)
    )
    if exclude_booking_id is not None:
        booked_count_query = booked_count_query.where(Booking.id != exclude_booking_id)

    booked_count = int(db.exec(booked_count_query).one())
    available_capacity = slot.capacity - booked_count
    if available_capacity < amount_of_people:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Selected time slot is not available for the requested party size. "
                f"Requested {amount_of_people} slot(s), but only {available_capacity} remain."
            ),
        )


def validate_service_for_booking(
    db: Session,
    service_id: UUID,
    itinerary_item_id: Optional[UUID],
    user_id: UUID,
    *,
    context: BookingCreationContext | None = None,
) -> tuple[Service, Optional[ItineraryItem]]:
    service = get_service_for_booking_or_404(db, service_id, context=context)
    if service.status != StatusTypes.active:
        raise HTTPException(
            status_code=400, detail="Only active services can be booked"
        )

    itinerary_item = None
    if itinerary_item_id is not None:
        itinerary_item, itinerary = get_owned_itinerary_item_context_cached_or_404(
            db,
            itinerary_item_id,
            user_id,
            context=context,
        )
        if service.listing_id != itinerary_item.listing_id:
            raise HTTPException(
                status_code=400,
                detail="Selected service does not belong to this itinerary item's listing",
            )

    return service, itinerary_item


def validate_service_capacity(
    db: Session,
    service: Service,
    booking_from_time: datetime,
    booking_to_time: datetime,
    amount_of_people: int,
) -> None:
    if service.capacity is None:
        return
    if amount_of_people < 1:
        raise HTTPException(
            status_code=400, detail="Amount of people must be at least 1"
        )
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


def calculate_hotel_days(booking_from_time: datetime, booking_to_time: datetime) -> int:
    """Calculate hotel nights using calendar dates, not floored elapsed hours."""
    nights = (booking_to_time.date() - booking_from_time.date()).days
    return max(1, nights)


def price_booking_from_itinerary_item(
    db: Session,
    itinerary_item_id: UUID,
    user_id: UUID,
    service: Service,
    amount_of_people: int,
    booking_from_time: Optional[datetime] = None,
    booking_to_time: Optional[datetime] = None,
    *,
    context: BookingCreationContext | None = None,
) -> dict:
    itinerary_item, itinerary = get_owned_itinerary_item_context_cached_or_404(
        db,
        itinerary_item_id,
        user_id,
        context=context,
    )

    # 3. Get pricing via PricingService using the selected service
    price_info = calculate_display_price_for_booking(
        db,
        service.listing_id,
        service.service_id,
        context=context,
    )
    base_price = float(price_info.get("base_price", 0.0))

    # Apply per-person pricing for non-hotel services
    is_hotel = (
        is_hotel_service(db, service)
        if context is None
        else is_hotel_service(db, service, context=context)
    )
    if not is_hotel:
        base_price = base_price * amount_of_people
    else:
        # For hotels, multiply by number of rooms and nights
        if booking_from_time and booking_to_time:
            hotel_days = calculate_hotel_days(booking_from_time, booking_to_time)
            base_price = base_price * amount_of_people * hotel_days

    service_fee_percent = float(price_info.get("service_fee_percent", 0.0))
    service_fee_amount = base_price * service_fee_percent
    display_price = base_price + service_fee_amount

    # 4. Auto-apply the active package discount whenever the itinerary qualifies.
    discount = get_eligible_package_discount_cached(db, itinerary, context=context)
    discount_percent = 0.0
    discount_amount = 0.0
    if discount is not None:
        discount_percent = normalize_discount_percent(
            getattr(discount, "discount_percent", 0.0)
        )
        max_discount_amount = getattr(discount, "max_discount_amount", None)
        discount_amount = calculate_discount_for_amount(
            display_price,
            discount_percent,
            max_discount_amount,
        )

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
    """Recalculate price for a booking based on current people count and stay duration.
    
    This ensures the price always reflects the actual booking details, not stale stored values.
    """
    # Retrieve booking to determine pricing path
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.service_id is None:
        raise HTTPException(
            status_code=400, detail="Booking is missing a linked service"
        )

    service = get_service_for_booking_or_404(db, booking.service_id)
    listing_id = service.listing_id

    # If tied to an itinerary item, use itinerary-based pricing
    if booking.itinerary_item_id is not None:
        people = getattr(booking, "amount_of_people", None) or 1
        return price_booking_from_itinerary_item(
            db,
            booking.itinerary_item_id,
            user_id,
            service,
            people,
            booking_from_time=booking.booking_from_time,
            booking_to_time=booking.booking_to_time,
        )

    # Standalone booking: recalculate from per-person/night price
    # This ensures price reflects current amount_of_people and hotel days
    price_info = calculate_display_price(db, listing_id, booking.service_id)
    per_person_base = float(price_info.get("base_price", 0.0))
    service_fee_percent = float(price_info.get("service_fee_percent", 0.10))
    
    is_hotel = is_hotel_service(db, service)
    people = getattr(booking, "amount_of_people", None) or 1
    
    if is_hotel:
        hotel_days = calculate_hotel_days(booking.booking_from_time, booking.booking_to_time)
        total_base = per_person_base * people * hotel_days
    else:
        total_base = per_person_base * people
    
    service_fee_amount = total_base * service_fee_percent
    display_price = total_base + service_fee_amount
    
    discount_percent = normalize_discount_percent(
        float(booking.discount_percent or 0.0)
    )
    discount_amount = float(booking.discount_amount or 0.0)
    final_price = display_price - discount_amount

    return {
        "base_price": total_base,
        "service_fee_percent": service_fee_percent,
        "service_fee_amount": service_fee_amount,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "display_price": display_price,
        "final_price": final_price,
    }


def create_booking(db: Session, booking: BookingCreate, user_id: UUID) -> Booking:
    return create_booking_record(db, booking, user_id, commit=True)


def create_booking_record(
    db: Session,
    booking: BookingCreate,
    user_id: UUID,
    *,
    commit: bool,
    context: BookingCreationContext | None = None,
) -> Booking:
    service, _ = validate_service_for_booking(
        db,
        booking.service_id,
        booking.itinerary_item_id,
        user_id,
        context=context,
    )
    slot: ServiceSlots | None = None
    booking_from_time = booking.booking_from_time
    booking_to_time = booking.booking_to_time
    is_virtual_slot = False

    if booking.service_slot_id is not None:
        slot, booking_from_time, booking_to_time = resolve_booking_slot_context(
            db,
            booking.service_id,
            booking.service_slot_id,
            booking_from_time,
            booking_to_time,
            context=context,
        )
        # Mark virtual slots so we don't store -1 in the FK column
        if slot is None and booking.service_slot_id == -1:
            is_virtual_slot = True
    else:
        if booking_requires_slot_selection(
            db,
            booking.service_id,
            booking_from_time,
            context=context,
        ):
            raise HTTPException(
                status_code=400,
                detail="Please select a service slot for the chosen date",
            )

    validate_booking_window(booking_from_time, booking_to_time)

    if slot is not None:
        validate_slot_capacity(
            db,
            slot,
            booking_from_time,
            booking_to_time,
            booking.amount_of_people or 1,
        )
    elif service.service_id is not None and service.capacity is not None:
        # Capacity fallback for services without explicit slots
        from app.modules.availability.service import get_booked_count

        booked_count = get_booked_count(
            db,
            service.service_id,
            booking_from_time,
            booking_to_time,
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
    booking_record.booking_from_time = booking_from_time
    booking_record.booking_to_time = booking_to_time
    # Virtual slots (id=-1) have no real ServiceSlots record - store NULL instead
    if is_virtual_slot:
        booking_record.service_slot_id = None
    if (
        is_restaurant_service(db, service)
        if context is None
        else is_restaurant_service(db, service, context=context)
    ):
        booking_record.status = BookingStatus.approved

    # If booking is tied to an itinerary item, calculate price accordingly
    price_breakdown: Optional[dict] = None
    if booking_record.itinerary_item_id is not None:
        price_breakdown = price_booking_from_itinerary_item(
            db,
            booking_record.itinerary_item_id,
            user_id,
            service,
            booking.amount_of_people or 1,
            booking_from_time=booking_from_time,
            booking_to_time=booking_to_time,
            context=context,
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
        price_breakdown = calculate_display_price_for_booking(
            db,
            service.listing_id,
            service.service_id,
            context=context,
        )
        # Determine if this is a hotel service for per-person pricing
        is_hotel = (
            is_hotel_service(db, service)
            if context is None
            else is_hotel_service(db, service, context=context)
        )
        people = booking.amount_of_people or 1

        # base_price from pricing service is per-person (or per-room for hotels)
        # Multiply by people to get total for this booking (or by nights for hotels)
        per_person_base = float(price_breakdown.get("base_price", 0))
        if is_hotel:
            hotel_days = calculate_hotel_days(booking_from_time, booking_to_time)
            total_base = per_person_base * people * hotel_days
        else:
            total_base = per_person_base * people

        service_fee_percent = float(price_breakdown.get("service_fee_percent", 0.10))
        service_fee_amount = total_base * service_fee_percent
        display_price = total_base + service_fee_amount
        final_price = display_price  # no discount for standalone

        booking_record.base_price = total_base
        booking_record.service_fee_percent = service_fee_percent
        booking_record.service_fee_amount = service_fee_amount
        booking_record.discount_percent = 0
        booking_record.discount_amount = 0
        booking_record.display_price = display_price
        booking_record.final_price = final_price

    db.add(booking_record)
    if commit:
        db.commit()
        db.refresh(booking_record)
    else:
        db.flush()
    return booking_record


def create_bulk_bookings(
    db: Session, items: List[BookingCreate], user_id: UUID
) -> List[Booking]:
    """Create multiple bookings atomically. All succeed or all fail."""
    bookings = []
    context = build_booking_creation_context(db, items)
    try:
        for booking_data in items:
            booking = create_booking_record(
                db,
                booking_data,
                user_id,
                commit=False,
                context=context,
            )
            bookings.append(booking)
        db.commit()
        for booking in bookings:
            db.refresh(booking)
        return bookings
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception(
            "Unexpected failure while creating bulk bookings for user %s", user_id
        )
        raise HTTPException(status_code=500, detail="Bulk booking failed")


def update_booking(db: Session, booking: Booking, update_data: dict) -> Booking:
    slot: ServiceSlots | None = None
    new_service_slot_id = update_data.get("service_slot_id", booking.service_slot_id)
    new_from_time = update_data.get("booking_from_time", booking.booking_from_time)
    new_to_time = update_data.get("booking_to_time", booking.booking_to_time)
    is_virtual_slot = False

    if booking.service_id is not None and new_service_slot_id is not None:
        slot, new_from_time, new_to_time = resolve_booking_slot_context(
            db,
            booking.service_id,
            new_service_slot_id,
            new_from_time,
            new_to_time,
        )
        update_data["booking_from_time"] = new_from_time
        update_data["booking_to_time"] = new_to_time
        # Mark virtual slots so we don't store -1 in the FK column
        if slot is None and new_service_slot_id == -1:
            is_virtual_slot = True
    elif booking.service_id is not None and (
        "booking_from_time" in update_data or "booking_to_time" in update_data
    ):
        if booking_requires_slot_selection(db, booking.service_id, new_from_time):
            raise HTTPException(
                status_code=400,
                detail="Please select a service slot for the chosen date",
            )

    time_changed = (
        new_from_time != booking.booking_from_time
        or new_to_time != booking.booking_to_time
    )
    slot_changed = new_service_slot_id != booking.service_slot_id
    people_changed = (
        "amount_of_people" in update_data
        and update_data["amount_of_people"] != booking.amount_of_people
    )

    if time_changed or slot_changed or people_changed:
        validate_booking_window(new_from_time, new_to_time)

        if time_changed:
            # Conflict check - only approved bookings block
            if booking.service_id is not None and check_booking_conflict(
                db,
                booking.service_id,
                new_from_time,
                new_to_time,
                exclude_booking_id=booking.id,
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Booking conflict: overlapping booking exists for service",
                )

        # Capacity check - count approved bookings overlapping with new time, excluding self
        if booking.service_id is not None and booking.service is not None:
            if slot is not None:
                validate_slot_capacity(
                    db,
                    slot,
                    new_from_time,
                    new_to_time,
                    update_data.get("amount_of_people", booking.amount_of_people or 1),
                    exclude_booking_id=booking.id,
                )
            elif booking.service.capacity is not None:
                booked_count = db.exec(
                    select(func.coalesce(func.sum(Booking.amount_of_people), 0))
                    .where(Booking.service_id == booking.service_id)
                    .where(Booking.status == BookingStatus.approved)
                    .where(Booking.id != booking.id)
                    .where(Booking.booking_from_time < new_to_time)
                    .where(Booking.booking_to_time > new_from_time)
                ).one_or_none()

                available = booking.service.capacity - int(booked_count)
                if available < (
                    update_data.get("amount_of_people", booking.amount_of_people or 1)
                ):
                    raise HTTPException(
                        status_code=409,
                        detail="Not enough capacity for requested time",
                    )
    else:
        validate_booking_window(
            update_data.get("booking_from_time", booking.booking_from_time),
            update_data.get("booking_to_time", booking.booking_to_time),
        )

    # Virtual slots (id=-1) have no real ServiceSlots record - store NULL instead
    if is_virtual_slot:
        update_data["service_slot_id"] = None

    for key, value in update_data.items():
        setattr(booking, key, value)

    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(
    db: Session,
    booking: Booking,
    *,
    cancelled_by_role: str | None = None,
    cancellation_reason: str | None = None,
) -> Booking:
    """
    Cancel a booking. If booking is approved and has payment, process refund first.
    If refund fails, booking stays approved and HTTPException is raised.
    """
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    if booking.status == BookingStatus.completed:
        raise HTTPException(
            status_code=400, detail="Completed bookings cannot be cancelled"
        )

    # If booking is approved AND has stripe_payment_intent_id, process refund first
    if booking.status == BookingStatus.approved and booking.stripe_payment_intent_id:
        # Import process_refund from stripe_payment
        from app.modules.stripe_payment.service import process_refund

        # Call process_refund - if it fails, raise error and DO NOT cancel
        refund_result = process_refund(db, booking)

        if not refund_result.get("success"):
            error_msg = refund_result.get("error", "Refund failed")
            raise HTTPException(status_code=400, detail=f"Cannot cancel: {error_msg}")

        # Refund succeeded - now cancel the booking

    # Update booking status to cancelled
    booking.status = BookingStatus.cancelled
    booking.cancelled_by_role = cancelled_by_role
    booking.cancellation_reason = cancellation_reason
    booking.cancelled_at = datetime.utcnow()

    db.commit()
    db.refresh(booking)
    return booking


def create_payment_intent(db: Session, booking_id: UUID, user_id: UUID) -> dict:
    """Delegate to stripe_payment service (imported from there)."""
    from app.modules.stripe_payment.service import (
        create_payment_intent as stripe_create_payment_intent,
    )

    return stripe_create_payment_intent(db, booking_id, user_id)


def delete_booking(db: Session, booking: Booking) -> None:
    """Delete a cancelled booking. Refunded bookings cannot be deleted."""
    if booking.status != BookingStatus.cancelled:
        raise HTTPException(
            status_code=400,
            detail="Only cancelled bookings can be deleted",
        )
    # Check if booking has a refund via PaymentEvent
    from app.modules.stripe_payment.models import PaymentEvent

    refund_event = db.exec(
        select(PaymentEvent).where(
            PaymentEvent.booking_id == booking.id,
            PaymentEvent.event_type.like("refund.%"),
        )
    ).first()
    if refund_event:
        raise HTTPException(
            status_code=400,
            detail="Refunded bookings cannot be deleted",
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
    return availability_is_available(
        db, service_id, capacity, start_dt, end_dt, requested_quantity
    )


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
