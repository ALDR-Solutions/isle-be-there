"""Service layer for availability module - CRUD and business logic."""

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime, time, date, timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlmodel import Session, col

from app.modules.availability.models import ListingHours, ServiceSlots
from app.modules.availability.schemas import (
    ListingHoursCreate,
    ListingHoursUpdate,
    ListingHoursResponse,
    ServiceSlotsCreate,
    ServiceSlotsUpdate,
    ServiceSlotsResponse,
    ServiceAvailableResponse,
    SlotAvailability,
    MassAvailabilityItem,
    MassAvailabilityResponse,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.businesses.models import BusinessType
from app.modules.listings.models import Listing
from app.modules.services.models import Service

HOTEL_DEFAULT_CHECK_IN_TIME = time(14, 0, 0)
HOTEL_DEFAULT_CHECK_OUT_TIME = time(11, 0, 0)


# ============================================================================
# ListingHours CRUD
# ============================================================================


def get_listing_hours(db: Session, listing_id: UUID, day: int) -> ListingHours | None:
    """Get listing hours for a specific day."""
    return (
        db.exec(
            select(ListingHours)
            .where(ListingHours.listing_id == listing_id)
            .where(ListingHours.day_of_week == day)
        )
        .scalars()
        .first()
    )


def list_listing_hours(db: Session, listing_id: UUID) -> list[ListingHours]:
    """List all hours for a listing."""
    return (
        db.exec(
            select(ListingHours)
            .where(ListingHours.listing_id == listing_id)
            .order_by(ListingHours.day_of_week)
        )
        .scalars()
        .all()
    )


def create_listing_hours(db: Session, data: ListingHoursCreate) -> ListingHours:
    """Create listing hours for a specific day."""
    # Check if hours already exist for this day
    existing = get_listing_hours(db, data.listing_id, data.day_of_week)
    if existing:
        raise HTTPException(409, f"Hours already exist for day {data.day_of_week}")

    hours = ListingHours(**data.model_dump())
    db.add(hours)
    db.commit()
    db.refresh(hours)
    return hours


def update_listing_hours(
    db: Session, listing_id: UUID, day: int, data: ListingHoursUpdate
) -> ListingHours:
    """Update hours for a specific day."""
    hours = get_listing_hours(db, listing_id, day)
    if not hours:
        raise HTTPException(404, f"No hours found for day {day}")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(hours, k, v)

    db.commit()
    db.refresh(hours)
    return hours


def delete_listing_hours(db: Session, listing_id: UUID, day: int) -> None:
    """Delete hours for a specific day."""
    hours = get_listing_hours(db, listing_id, day)
    if not hours:
        raise HTTPException(404, f"No hours found for day {day}")

    db.delete(hours)
    db.commit()


# ============================================================================
# ServiceSlots CRUD
# ============================================================================


def get_service_slot(db: Session, slot_id: int) -> ServiceSlots | None:
    """Get a service slot by ID."""
    return (
        db.exec(select(ServiceSlots).where(ServiceSlots.id == slot_id))
        .scalars()
        .first()
    )


def get_service_slot_for_service(
    db: Session,
    service_id: UUID,
    slot_id: int,
) -> ServiceSlots | None:
    """Get a service slot scoped to a specific service."""
    return (
        db.exec(
            select(ServiceSlots)
            .where(ServiceSlots.id == slot_id)
            .where(ServiceSlots.service_id == service_id)
        )
        .scalars()
        .first()
    )


def list_service_slots(db: Session, service_id: UUID) -> list[ServiceSlots]:
    """List all slots for a service."""
    service = get_service_record(db, service_id)
    if service and is_hotel_service(db, service_id):
        return []

    return (
        db.exec(
            select(ServiceSlots)
            .where(ServiceSlots.service_id == service_id)
            .order_by(ServiceSlots.day_of_week, ServiceSlots.start_time)
        )
        .scalars()
        .all()
    )


def create_service_slot(db: Session, data: ServiceSlotsCreate) -> ServiceSlots:
    """Create a new service slot."""
    # Get the service to find its listing_id
    service = get_service_record(db, data.service_id)
    if not service:
        raise HTTPException(404, "Service not found")
    ensure_service_supports_slots(db, service)

    # Validate slot is within listing hours for the same day
    validate_slot_within_listing_hours(
        db,
        data.service_id,
        service.listing_id,
        data.day_of_week,
        data.start_time,
        data.end_time,
    )

    # Check for overlapping slots
    check_slot_overlap(
        db, data.service_id, data.day_of_week, data.start_time, data.end_time
    )

    slot = ServiceSlots(**data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def update_service_slot(
    db: Session,
    service_id: UUID,
    slot_id: int,
    data: ServiceSlotsUpdate,
) -> ServiceSlots:
    """Update an existing service slot."""
    slot = get_service_slot_for_service(db, service_id, slot_id)
    if not slot:
        raise HTTPException(404, "Slot not found")

    service = get_service_record(db, service_id)
    if not service:
        raise HTTPException(404, "Service not found")
    ensure_service_supports_slots(db, service)

    payload = data.model_dump(exclude_unset=True)
    next_day = payload.get("day_of_week", slot.day_of_week)
    next_start = payload.get("start_time", slot.start_time)
    next_end = payload.get("end_time", slot.end_time)
    next_capacity = payload.get("capacity", slot.capacity)

    future_linked_bookings = (
        db.exec(
            select(Booking)
            .where(Booking.service_slot_id == slot.id)
            .where(
                col(Booking.status).in_([BookingStatus.pending, BookingStatus.approved])
            )
            .where(Booking.booking_to_time >= datetime.utcnow())
        )
        .scalars()
        .all()
    )

    schedule_changed = (
        next_day != slot.day_of_week
        or next_start != slot.start_time
        or next_end != slot.end_time
    )
    if schedule_changed and future_linked_bookings:
        raise HTTPException(
            409,
            "Cannot change this slot's day or time while future bookings are linked to it",
        )

    if next_capacity < slot.capacity:
        approved_booking_loads = db.exec(
            select(
                Booking.booking_from_time,
                Booking.booking_to_time,
                func.coalesce(func.sum(Booking.amount_of_people), 0),
            )
            .where(Booking.service_slot_id == slot.id)
            .where(Booking.status == BookingStatus.approved)
            .where(Booking.booking_to_time >= datetime.utcnow())
            .group_by(Booking.booking_from_time, Booking.booking_to_time)
        ).all()

        if any(
            int(booked_people) > next_capacity
            for _, _, booked_people in approved_booking_loads
        ):
            raise HTTPException(
                409,
                "Cannot reduce slot capacity below approved bookings already assigned to this slot",
            )

    validate_slot_within_listing_hours(
        db,
        service_id,
        service.listing_id,
        next_day,
        next_start,
        next_end,
    )
    check_slot_overlap(
        db,
        service_id,
        next_day,
        next_start,
        next_end,
        exclude_id=slot.id,
    )

    for key, value in payload.items():
        setattr(slot, key, value)

    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def delete_service_slot(db: Session, service_id: UUID, slot_id: int) -> None:
    """Delete a service slot."""
    slot = get_service_slot_for_service(db, service_id, slot_id)
    if not slot:
        raise HTTPException(404, "Slot not found")

    db.delete(slot)
    db.commit()


# ============================================================================
# Slot Validation
# ============================================================================


def validate_slot_within_listing_hours(
    db: Session,
    service_id: UUID,
    listing_id: UUID,
    day: int,
    start_time: time,
    end_time: time,
) -> None:
    """Validate that a slot falls within the listing's hours for the same day."""
    listing_hours = get_listing_hours(db, listing_id, day)
    if not listing_hours:
        raise HTTPException(422, f"No listing hours defined for day {day}")

    if start_time < listing_hours.open_time or end_time > listing_hours.close_time:
        raise HTTPException(
            422,
            f"Slot times must be within listing hours ({listing_hours.open_time} to {listing_hours.close_time})",
        )


def check_slot_overlap(
    db: Session,
    service_id: UUID,
    day: int,
    start_time: time,
    end_time: time,
    exclude_id: int | None = None,
) -> None:
    """Check if a slot overlaps with existing slots for the same service and day."""
    query = (
        select(ServiceSlots)
        .where(ServiceSlots.service_id == service_id)
        .where(ServiceSlots.day_of_week == day)
        # Overlap: existing slot starts before new end AND ends after new start
        .where(ServiceSlots.start_time < end_time)
        .where(ServiceSlots.end_time > start_time)
    )

    if exclude_id:
        query = query.where(ServiceSlots.id != exclude_id)

    overlapping = db.exec(query).scalars().first()
    if overlapping:
        raise HTTPException(
            422,
            f"Slot overlaps with existing slot ({overlapping.start_time} to {overlapping.end_time})",
        )


# ============================================================================
# Availability Query Functions
# ============================================================================


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
        .where(
            col(Booking.status).notin_(
                [
                    BookingStatus.cancelled,
                    BookingStatus.pending,
                ]
            )
        )
        .where(Booking.booking_from_time < end_dt)
        .where(Booking.booking_to_time > start_dt)
    ).scalar_one()
    return int(result)


def get_slot_remaining_capacity(
    db: Session,
    service_id: UUID,
    slot_id: int,
    slot_date: datetime,
) -> int:
    """
    Calculate remaining capacity for a slot on a specific date.
    Uses the ServiceSlots.capacity and counts confirmed bookings for that time window.
    """
    slot = get_service_slot(db, slot_id)
    if not slot:
        return 0

    slot_date_only = slot_date.date()
    start_dt = datetime.combine(slot_date_only, slot.start_time)
    end_dt = datetime.combine(slot_date_only, slot.end_time)

    booked = get_booked_count(db, service_id, start_dt, end_dt)
    return max(0, slot.capacity - booked)


def is_slot_available(
    db: Session,
    service_id: UUID,
    slot_id: int,
    slot_date: datetime,
    requested_count: int = 1,
) -> bool:
    """Check if a slot has enough remaining capacity for the requested count."""
    remaining = get_slot_remaining_capacity(db, service_id, slot_id, slot_date)
    return remaining >= requested_count


def get_available_slots(
    db: Session,
    service_id: UUID,
    capacity: int,
    start_dt: datetime,
    end_dt: datetime,
) -> int:
    """Calculate available slots (capacity minus booked)."""
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
    """Check if service is available for requested quantity."""
    return (
        get_available_slots(db, service_id, capacity, start_dt, end_dt)
        >= requested_quantity
    )


# ============================================================================
# Hotel Service Detection
# ============================================================================


def is_hotel_service(db: Session, service_id: UUID) -> bool:
    """
    Traverse Service → Listing → BusinessType to determine if this is a hotel service.
    Returns True if BusinessType.name contains 'hotel' (case-insensitive).
    """
    service = (
        db.exec(select(Service).where(Service.service_id == service_id))
        .scalars()
        .first()
    )
    if not service or not service.listing_id:
        return False

    listing = (
        db.exec(select(Listing).where(Listing.id == service.listing_id))
        .scalars()
        .first()
    )
    if not listing or not listing.business_type:
        return False

    business_type = (
        db.exec(select(BusinessType).where(BusinessType.id == listing.business_type))
        .scalars()
        .first()
    )
    if not business_type or not business_type.name:
        return False

    return business_type.name.lower() == "hotel"


def get_service_record(db: Session, service_id: UUID) -> Service | None:
    return (
        db.exec(select(Service).where(Service.service_id == service_id))
        .scalars()
        .first()
    )


def ensure_service_supports_slots(db: Session, service: Service) -> None:
    if is_hotel_service(db, service.service_id):
        raise HTTPException(400, "Hotel services do not support service slots")


# ============================================================================
# Service Availability Query
# ============================================================================


def get_service_availability(
    db: Session,
    service_id: UUID,
    date: date,
    people: int,
) -> ServiceAvailableResponse:
    """
    Get availability for a service on a specific date for a party size.
    Returns is_open=False with closed_reason='no_listing_hours' if no slots found.
    For hotels, checks remaining >= 1; for non-hotels, checks remaining >= people.
    If all slots are unavailable, sets closed_reason='fully_booked'.
    """
    # 1. Fetch Service to get listing_id
    service = get_service_record(db, service_id)
    python_weekday = date.weekday()
    db_day_of_week = (python_weekday + 1) % 7  # Convert Monday-based to Sunday-based
    if not service:
        # Return empty availability instead of 404 - treats deleted service as "unavailable"
        return ServiceAvailableResponse(
            service_id=service_id,
            date=date.isoformat(),
            day_of_week=db_day_of_week,
            is_available=False,
            is_open=False,
            slots=[],
            closed_reason="service_not_found",
        )

    # 2. Determine if hotel via is_hotel_service()
    is_hotel = is_hotel_service(db, service_id)
    service_capacity = service.capacity if service.capacity is not None else 999

    if is_hotel:
        start_dt = datetime.combine(date, HOTEL_DEFAULT_CHECK_IN_TIME)
        end_dt = datetime.combine(date + timedelta(days=1), HOTEL_DEFAULT_CHECK_OUT_TIME)
        remaining = get_available_slots(
            db,
            service_id,
            service_capacity,
            start_dt,
            end_dt,
        )
        is_open = remaining >= 1
        return ServiceAvailableResponse(
            service_id=service_id,
            date=date.isoformat(),
            day_of_week=db_day_of_week,
            is_available=is_open,
            is_open=is_open,
            slots=[],
            closed_reason=None if is_open else "fully_booked",
        )

    # 3. Get day-of-week from date (Python: 0=Monday, 6=Sunday; DB: 0=Sunday, 6=Saturday)
    # Convert: Python weekday() returns 0=Monday, DB wants 0=Sunday
    # 4. Fetch ServiceSlots for that service + day-of-week
    slots = (
        db.exec(
            select(ServiceSlots)
            .where(ServiceSlots.service_id == service_id)
            .where(ServiceSlots.day_of_week == db_day_of_week)
        )
        .scalars()
        .all()
    )

    # 5. If no slots found, try falling back to listing hours
    if not slots:
        # Get listing hours for this day
        listing_hours = get_listing_hours(db, service.listing_id, db_day_of_week)
        if listing_hours:
            # Create virtual slot from listing hours using namedtuple
            VirtualSlot = namedtuple(
                "VirtualSlot",
                [
                    "id",
                    "service_id",
                    "day_of_week",
                    "start_time",
                    "end_time",
                    "capacity",
                    "is_virtual",
                ],
            )
            slots = [
                VirtualSlot(
                    id=-1,  # Virtual slot ID
                    service_id=service_id,
                    day_of_week=db_day_of_week,
                    start_time=listing_hours.open_time,
                    end_time=listing_hours.close_time,
                    capacity=service_capacity,  # Use service capacity
                    is_virtual=True,  # Mark as virtual slot
                )
            ]
        else:
            # No slots and no listing hours - service is available anytime (24h)
            from datetime import time as time_class

            VirtualSlot = namedtuple(
                "VirtualSlot",
                [
                    "id",
                    "service_id",
                    "day_of_week",
                    "start_time",
                    "end_time",
                    "capacity",
                    "is_virtual",
                ],
            )
            slots = [
                VirtualSlot(
                    id=-1,  # Virtual slot ID
                    service_id=service_id,
                    day_of_week=db_day_of_week,
                    start_time=time_class(0, 0, 0),  # 00:00:00
                    end_time=time_class(23, 59, 59),  # 23:59:59
                    capacity=service_capacity,  # Use service capacity
                    is_virtual=True,
                )
            ]

    # 6. For each slot, call get_slot_remaining_capacity()
    slot_availabilities = []
    all_unavailable = True

    for slot in slots:
        slot_date = datetime.combine(date, slot.start_time)

        start_dt = datetime.combine(date, slot.start_time)
        end_dt = datetime.combine(date, slot.end_time)

        # For virtual slots (from listing hours fallback), use service capacity minus overlapping bookings
        if getattr(slot, "is_virtual", False):
            remaining = get_available_slots(
                db,
                service_id,
                slot.capacity,
                start_dt,
                end_dt,
            )
        else:
            remaining = get_slot_remaining_capacity(db, service_id, slot.id, slot_date)

        # 7. Set is_available: for hotels remaining >= 1, for non-hotels remaining >= people
        required = 1 if is_hotel else people
        is_available = remaining >= required

        if is_available:
            all_unavailable = False

        slot_availabilities.append(
            SlotAvailability(
                slot_id=slot.id,
                day_of_week=db_day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
                capacity=slot.capacity,
                remaining_capacity=remaining,
                is_available=is_available,
            )
        )

    # 8. If ALL slots have is_available: false, set closed_reason: 'fully_booked'
    closed_reason = "fully_booked" if all_unavailable else None

    # 9. Return ServiceAvailableResponse
    return ServiceAvailableResponse(
        service_id=service_id,
        date=date.isoformat(),
        day_of_week=db_day_of_week,
        is_available=not all_unavailable,
        is_open=not all_unavailable,
        slots=slot_availabilities,
        closed_reason=closed_reason,
    )


def get_mass_availability(
    db: Session,
    service_id: UUID,
    start_date: date,
    end_date: date,
    people: int,
) -> MassAvailabilityResponse:
    """
    Get availability for a service across a date range (lightweight, no slot details).
    For each date, checks if the service has any availability (open slots or capacity).
    Returns is_open=false for past dates or dates with no availability.
    """
    availability_items = []
    current_date = start_date
    today = date.today()

    while current_date <= end_date:
        if current_date < today:
            availability_items.append(
                MassAvailabilityItem(
                    date=current_date.isoformat(),
                    is_open=False,
                )
            )
        else:
            try:
                service_avail = get_service_availability(
                    db, service_id, current_date, people
                )
                availability_items.append(
                    MassAvailabilityItem(
                        date=current_date.isoformat(),
                        is_open=service_avail.is_open,
                    )
                )
            except Exception:
                availability_items.append(
                    MassAvailabilityItem(
                        date=current_date.isoformat(),
                        is_open=False,
                    )
                )
        current_date = current_date + timedelta(days=1)

    return MassAvailabilityResponse(
        service_id=service_id,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        availability=availability_items,
    )
