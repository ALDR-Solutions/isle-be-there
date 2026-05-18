"""Service layer for availability module - CRUD and business logic."""

from datetime import datetime, time
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlmodel import Session, col

from app.modules.availability.models import ListingHours, ServiceSlots
from app.modules.availability.schemas import (
    ListingHoursCreate,
    ListingHoursUpdate,
    ListingHoursResponse,
    ServiceSlotsCreate,
    ServiceSlotsUpdate,
    ServiceSlotsResponse,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.listings.models import Listing
from app.modules.services.models import Service


# ============================================================================
# ListingHours CRUD
# ============================================================================


def get_listing_hours(db: Session, listing_id: UUID, day: int) -> ListingHours | None:
    """Get listing hours for a specific day."""
    return db.exec(
        select(ListingHours)
        .where(ListingHours.listing_id == listing_id)
        .where(ListingHours.day_of_week == day)
    ).scalars().first()


def list_listing_hours(db: Session, listing_id: UUID) -> list[ListingHours]:
    """List all hours for a listing."""
    return db.exec(
        select(ListingHours)
        .where(ListingHours.listing_id == listing_id)
        .order_by(ListingHours.day_of_week)
    ).scalars().all()


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


def update_listing_hours(db: Session, listing_id: UUID, day: int, data: ListingHoursUpdate) -> ListingHours:
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
    return db.exec(select(ServiceSlots).where(ServiceSlots.id == slot_id)).scalars().first()


def list_service_slots(db: Session, service_id: UUID) -> list[ServiceSlots]:
    """List all slots for a service."""
    return db.exec(
        select(ServiceSlots)
        .where(ServiceSlots.service_id == service_id)
        .order_by(ServiceSlots.day_of_week, ServiceSlots.start_time)
    ).scalars().all()


def create_service_slot(db: Session, data: ServiceSlotsCreate) -> ServiceSlots:
    """Create a new service slot."""
    # Get the service to find its listing_id
    service = db.exec(select(Service).where(Service.service_id == data.service_id)).scalars().first()
    if not service:
        raise HTTPException(404, "Service not found")

    # Validate slot is within listing hours for the same day
    _validate_slot_within_listing_hours(db, data.service_id, service.listing_id, data.day_of_week, data.start_time, data.end_time)

    # Check for overlapping slots
    _check_slot_overlap(db, data.service_id, data.day_of_week, data.start_time, data.end_time)

    slot = ServiceSlots(**data.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


def delete_service_slot(db: Session, slot_id: int) -> None:
    """Delete a service slot."""
    slot = get_service_slot(db, slot_id)
    if not slot:
        raise HTTPException(404, "Slot not found")

    db.delete(slot)
    db.commit()


# ============================================================================
# Slot Validation
# ============================================================================


def _validate_slot_within_listing_hours(
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
            f"Slot times must be within listing hours ({listing_hours.open_time} to {listing_hours.close_time})"
        )


def _check_slot_overlap(
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
        raise HTTPException(422, f"Slot overlaps with existing slot ({overlapping.start_time} to {overlapping.end_time})")


# ============================================================================
# Availability Query Functions
# ============================================================================


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

    # Build datetime window for this slot on the given date
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
        .where(Booking.booking_from_time < end_dt)
        .where(Booking.booking_to_time > start_dt)
    ).scalar_one()
    return int(result)


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
    return get_available_slots(db, service_id, capacity, start_dt, end_dt) >= requested_quantity