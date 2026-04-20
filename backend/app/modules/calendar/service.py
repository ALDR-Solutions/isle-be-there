from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from app.modules.bookings.models import Booking
from app.modules.itineraries.model import Itinerary, ItineraryItem
from app.modules.services.models import Service
from app.modules.listings.models import Listing

from .schemas import CalendarEventResponse


def list_calendar_events(
    db: Session,
    user_id: UUID,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[CalendarEventResponse]:
    start = _normalize_timestamp(start)
    end = _normalize_timestamp(end)
    booking_events = _load_booking_events(db, user_id, start, end)
    itinerary_events = _load_itinerary_events(db, user_id, start, end)
    events = booking_events + itinerary_events
    return sorted(events, key=lambda event: (event.start, event.title))


def _load_booking_events(
    db: Session,
    user_id: UUID,
    start: datetime | None,
    end: datetime | None,
) -> list[CalendarEventResponse]:
    query = select(Booking).where(Booking.user_id == user_id)

    if start is not None:
        query = query.where(Booking.booking_to_time >= start)
    if end is not None:
        query = query.where(Booking.booking_from_time <= end)

    bookings = db.exec(query).all()
    if not bookings:
        return []

    service_ids = {booking.service_id for booking in bookings if booking.service_id is not None}
    services = db.exec(select(Service).where(Service.service_id.in_(service_ids))).all() if service_ids else []
    services_by_id = {service.service_id: service for service in services}

    listing_ids = {
        listing_id
        for listing_id in (
            [booking.listing_id for booking in bookings]
            + [service.listing_id for service in services]
        )
        if listing_id is not None
    }
    listings = db.exec(select(Listing).where(Listing.id.in_(listing_ids))).all() if listing_ids else []
    listings_by_id = {listing.id: listing for listing in listings}

    events: list[CalendarEventResponse] = []
    for booking in bookings:
        service = services_by_id.get(booking.service_id) if booking.service_id else None
        listing_id = booking.listing_id or (service.listing_id if service else None)
        listing = listings_by_id.get(listing_id) if listing_id else None
        status = _booking_status_value(booking.status)

        title_parts = ["Booking"]
        if service and service.name:
            title_parts.append(service.name)
        elif listing and listing.title:
            title_parts.append(listing.title)

        events.append(
            CalendarEventResponse(
                id=f"booking-{booking.id}",
                source="booking",
                title=": ".join(title_parts),
                start=booking.booking_from_time,
                end=booking.booking_to_time,
                status=status,
                color=_booking_color(status),
                listing_id=listing_id,
                service_id=booking.service_id,
                booking_id=booking.id,
                details={
                    "bookers_name": booking.bookers_name,
                    "amount_of_people": booking.amount_of_people,
                    "special_requests": booking.special_requests,
                    "listing_title": listing.title if listing else None,
                    "service_name": service.name if service else None,
                },
            )
        )

    return events


def _load_itinerary_events(
    db: Session,
    user_id: UUID,
    start: datetime | None,
    end: datetime | None,
) -> list[CalendarEventResponse]:
    query = (
        select(ItineraryItem, Itinerary)
        .join(Itinerary, Itinerary.id == ItineraryItem.itinerary_id)
        .where(Itinerary.user_id == user_id)
        .where(Itinerary.status != "archived")
    )

    if start is not None:
        query = query.where(ItineraryItem.end_at >= start)
    if end is not None:
        query = query.where(ItineraryItem.start_at <= end)

    rows = db.exec(query).all()
    events: list[CalendarEventResponse] = []

    for row in rows:
        item: ItineraryItem = row[0]
        itinerary: Itinerary = row[1]
        events.append(
            CalendarEventResponse(
                id=f"itinerary-{item.id}",
                source="itinerary",
                title=item.title,
                start=item.start_at,
                end=item.end_at,
                status=itinerary.status,
                color=_itinerary_color(itinerary.status),
                listing_id=item.listing_id,
                booking_id=item.linked_booking_id,
                itinerary_id=itinerary.id,
                itinerary_item_id=item.id,
                details={
                    "itinerary_title": itinerary.title,
                    "item_type": item.item_type,
                    "estimated_cost": float(item.estimated_cost or 0),
                    "reason_tags": list(item.reason_tags or []),
                    "address_snapshot": item.address_snapshot,
                    "extra_metadata": item.extra_metadata,
                },
            )
        )

    return events


def _booking_status_value(status) -> str:
    return status.value if hasattr(status, "value") else str(status)


def _booking_color(status: str) -> str:
    if status == "approved":
        return "#16a34a"
    if status == "pending":
        return "#d97706"
    if status == "cancelled":
        return "#dc2626"
    if status == "completed":
        return "#0891b2"
    return "#475569"


def _itinerary_color(status: str) -> str:
    if status == "draft":
        return "#2563eb"
    if status == "saved":
        return "#7c3aed"
    return "#64748b"


def _normalize_timestamp(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.replace(tzinfo=None)
