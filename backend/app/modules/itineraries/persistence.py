from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, desc
from sqlmodel import Session, select

from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.service import create_booking as booking_service_create
from app.modules.discounts.service import check_package_discount_eligibility
from app.modules.services.models import Service, StatusTypes as ServiceStatusTypes
from app.shared.domain import get_owned_itinerary_or_404

from .models import (
    Itinerary,
    ItineraryItem,
    ItineraryItemStatus,
    ItineraryStatus as ItineraryModelStatus,
)
from .planner import plan_itinerary, resolved_end_date
from .schemas import (
    ItinerarySaveRequest,
    ItineraryStatus as ItinerarySchemaStatus,
    SavedItineraryResponse,
    SavedItinerarySummaryResponse,
)
from .serialization import (
    build_items_for_saved_itinerary,
    serialize_saved_itinerary,
    status_value,
)


def list_saved_itineraries(
    db: Session,
    user_id: UUID,
) -> list[SavedItinerarySummaryResponse]:
    itineraries = db.exec(
        select(Itinerary)
        .where(Itinerary.user_id == user_id)
        .where(Itinerary.status == ItineraryModelStatus.SAVED)
        .order_by(desc(Itinerary.created_at))
    ).all()

    if not itineraries:
        return []

    itinerary_ids = [itinerary.id for itinerary in itineraries]
    item_rows = db.exec(
        select(ItineraryItem).where(
            ItineraryItem.__table__.c.itinerary_id.in_(itinerary_ids)
        )
    ).all()

    item_counts: dict[UUID, int] = {itinerary_id: 0 for itinerary_id in itinerary_ids}
    for item in item_rows:
        item_counts[item.itinerary_id] = item_counts.get(item.itinerary_id, 0) + 1

    return [
        SavedItinerarySummaryResponse(
            id=itinerary.id,
            title=itinerary.title,
            status=ItinerarySchemaStatus(status_value(itinerary.status)),
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            total_estimated_cost=float(itinerary.total_estimated_cost or 0),
            item_count=item_counts.get(itinerary.id, 0),
            created_at=itinerary.created_at,
        )
        for itinerary in itineraries
    ]


def get_saved_itinerary(
    db: Session,
    user_id: UUID,
    itinerary_id: UUID,
) -> SavedItineraryResponse:
    itinerary = get_owned_itinerary_or_404(db, itinerary_id, user_id)
    items = db.exec(
        select(ItineraryItem)
        .where(ItineraryItem.itinerary_id == itinerary.id)
        .order_by(
            ItineraryItem.day_date,
            ItineraryItem.sort_order,
            ItineraryItem.start_at,
        )
    ).all()
    return serialize_saved_itinerary(itinerary, items)


def save_itinerary(
    db: Session,
    user_id: UUID,
    payload: ItinerarySaveRequest,
) -> SavedItineraryResponse:
    planned = plan_itinerary(db, payload.plan_request, user_id)
    if len(planned.days) != payload.plan_request.resolved_trip_days:
        raise HTTPException(
            status_code=400,
            detail="Saved itinerary does not match requested trip length",
        )

    try:
        itinerary = Itinerary(
            user_id=user_id,
            title=resolved_title(payload),
            start_date=payload.plan_request.start_date,
            end_date=resolved_end_date(payload.plan_request),
            status=payload.status.value,
            budget_level=payload.plan_request.budget_level.value,
            pace=payload.plan_request.pace.value,
            country=payload.plan_request.country,
            interests=payload.plan_request.interests,
            total_estimated_cost=float(planned.total_estimated_cost),
        )
        db.add(itinerary)
        db.flush()

        items = build_items_for_saved_itinerary(itinerary.id, planned)
        for item in items:
            db.add(item)

        db.commit()
        db.refresh(itinerary)
        saved_items = db.exec(
            select(ItineraryItem)
            .where(ItineraryItem.itinerary_id == itinerary.id)
            .order_by(
                ItineraryItem.day_date,
                ItineraryItem.sort_order,
                ItineraryItem.start_at,
            )
        ).all()
    except Exception:
        db.rollback()
        raise

    return serialize_saved_itinerary(itinerary, saved_items)


def delete_saved_itinerary(db: Session, user_id: UUID, itinerary_id: UUID) -> None:
    itinerary = get_owned_itinerary_or_404(db, itinerary_id, user_id)

    try:
        # Delete child rows first so SQLAlchemy does not attempt to null out
        # itinerary_items.itinerary_id, which is a required foreign key.
        db.exec(
            delete(ItineraryItem).where(ItineraryItem.itinerary_id == itinerary.id)
        )
        db.delete(itinerary)
        db.commit()
    except Exception:
        db.rollback()
        raise


def create_itinerary(db: Session, user_id: UUID, data: dict) -> Itinerary:
    items_data = data.pop("items", [])
    total_cost = sum(item.get("estimated_cost", 0) for item in items_data)

    itinerary = Itinerary(
        user_id=user_id,
        status=ItineraryModelStatus.DRAFT,
        total_estimated_cost=total_cost,
        **data,
    )
    db.add(itinerary)
    db.flush()

    for item_data in items_data:
        item = ItineraryItem(
            itinerary_id=itinerary.id,
            status=ItineraryItemStatus.PLANNED,
            **item_data,
        )
        db.add(item)

    db.commit()
    db.refresh(itinerary)
    return itinerary


def get_itinerary_by_id(db: Session, itinerary_id: UUID, user_id: UUID) -> Itinerary:
    return get_owned_itinerary_or_404(db, itinerary_id, user_id, load_items=True)


def confirm_itinerary(db: Session, itinerary_id: UUID, user_id: UUID) -> dict:
    itinerary = get_itinerary_by_id(db, itinerary_id, user_id)

    if itinerary.status != ItineraryModelStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail="Only DRAFT itineraries can be confirmed",
        )

    discount_info = check_package_discount_eligibility(db, itinerary)
    discount_applied = False
    discount_amount = 0.0

    if discount_info.get("eligible"):
        discount = discount_info["discount"]
        discount_amount = discount_info.get("estimated_discount", 0)
        itinerary.applied_discount_id = discount.id
        itinerary.discount_amount = discount_amount
        discount_applied = True

    itinerary.status = ItineraryModelStatus.CONFIRMED
    db.commit()
    db.refresh(itinerary)

    return {
        "itinerary": itinerary,
        "discount_applied": discount_applied,
        "discount_amount": discount_amount,
    }


def convert_itinerary_to_bookings(
    db: Session,
    itinerary_id: UUID,
    user_id: UUID,
    item_ids: list[UUID] | None = None,
) -> Itinerary:
    itinerary = get_itinerary_by_id(db, itinerary_id, user_id)

    if itinerary.status != ItineraryModelStatus.CONFIRMED:
        raise HTTPException(
            status_code=400,
            detail="Only CONFIRMED itineraries can be converted to bookings",
        )

    items = itinerary.items
    if item_ids is not None:
        items = [item for item in items if item.id in item_ids]

    all_booked = True
    for item in items:
        if item.linked_booking_id is not None:
            continue

        service = db.exec(
            select(Service)
            .where(Service.listing_id == item.listing_id)
            .where(Service.status == ServiceStatusTypes.active)
            .order_by(Service.created_at)
        ).first()
        if not service:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Cannot convert itinerary item to booking without an active service"
                ),
            )

        booking_data = BookingCreate(
            service_id=service.service_id,
            itinerary_item_id=item.id,
            booking_from_time=item.start_at,
            booking_to_time=item.end_at,
        )
        booking = booking_service_create(db, booking_data, user_id)

        item.linked_booking_id = booking.id
        item.status = ItineraryItemStatus.BOOKED
        db.add(item)

        if booking.status.value == "cancelled":
            all_booked = False

    if all_booked and items:
        itinerary.status = ItineraryModelStatus.COMPLETED

    db.commit()
    db.refresh(itinerary)
    return itinerary


def resolved_title(payload: ItinerarySaveRequest) -> str:
    if payload.title and payload.title.strip():
        return payload.title.strip()

    location = payload.plan_request.country or "Trip"
    return f"{location} itinerary"
