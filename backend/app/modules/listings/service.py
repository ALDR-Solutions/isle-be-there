"""Business logic for listings."""

from datetime import datetime
import random
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from shapely.geometry import Point
from sqlmodel import Session, asc, col, desc, select

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.interests.models import ListingInterest, UserInterest, BusinessTypeInterest
from app.modules.interests.models import ListingInterest, UserInterest
from app.modules.listings.schemas import ListingCreate
from app.modules.reviews.models import Review
from app.modules.services.models import Service, StatusTypes as ServiceStatusTypes
from app.shared.domain import (
    ensure_listing_belongs_to_business,
    get_business_by_user_id,
    get_listing_or_404,
)
from app.shared.services import extract_lat_lng, build_location

from .models import Listing, Statuses

ACTIVE_LIKE_STATUSES = (Statuses.active, Statuses.approved)


def batch_review_stats(db: Session, listing_ids: list) -> dict:
    if not listing_ids:
        return {}

    rows = db.exec(
        select(
            Review.listing_id,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .where(Review.listing_id.in_(listing_ids))
        .group_by(Review.listing_id)
    ).all()

    stats = {
        row.listing_id: {
            "avg_rating": float(row.avg_rating) if row.avg_rating is not None else None,
            "review_count": int(row.review_count or 0),
        }
        for row in rows
    }

    for listing_id in listing_ids:
        stats.setdefault(
            listing_id,
            {"avg_rating": None, "review_count": 0}
        )

    return stats


def normalize_interest_ids(interest_ids: list[UUID] | None) -> list[UUID]:
    if not interest_ids:
        return []

    deduplicated: list[UUID] = []
    seen: set[UUID] = set()
    for interest_id in interest_ids:
        if interest_id in seen:
            continue
        seen.add(interest_id)
        deduplicated.append(interest_id)
    return deduplicated


def get_allowed_interest_ids(db: Session, business_type_id: UUID | None) -> set[UUID]:
    if not business_type_id:
        return set()

    rows = db.exec(
        select(BusinessTypeInterest.interest_id).where(
            BusinessTypeInterest.business_type_id == business_type_id
        )
    ).all()
    return set(rows)


def validate_interest_ids_for_business_type(
    db: Session,
    business_type_id: UUID | None,
    interest_ids: list[UUID] | None,
) -> list[UUID]:
    normalized_interest_ids = normalize_interest_ids(interest_ids)
    if not normalized_interest_ids:
        return []

    allowed_interest_ids = get_allowed_interest_ids(db, business_type_id)
    invalid_interest_ids = [
        str(interest_id)
        for interest_id in normalized_interest_ids
        if interest_id not in allowed_interest_ids
    ]
    if invalid_interest_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interests for this listing type: {', '.join(invalid_interest_ids)}",
        )

    return normalized_interest_ids


def sync_listing_interests(db: Session, listing_id: UUID, interest_ids: list[UUID]) -> None:
    """
    Synchronize the interests associated with a listing by adding new interests and removing old ones.

    This function performs a synchronization between the current interests in the database for a given
    listing and the target set of interest IDs provided. It removes any existing interests that are not
    in the target set and adds any new interests that are not already associated with the listing.

    Args:
        db (Session): The database session for executing database operations.
        listing_id (UUID): The unique identifier of the listing to synchronize interests for.
        interest_ids (list[UUID]): The list of interest IDs that should be associated with the listing.

    Returns:
        None: This function modifies the database directly and does not return any value.

    Notes:
        - The function handles special characters in interest data, including:
          * Tab character (\t)
          * Carriage return (\r)
          * Newline character (\n)
        - The operation is performed in a single transaction within the provided database session.
    """
    existing_rows = db.exec(
        select(ListingInterest).where(ListingInterest.listing_id == listing_id)
    ).all()
    existing_interest_ids = {row.interest_id for row in existing_rows}
    target_interest_ids = set(interest_ids)

    for row in existing_rows:
        if row.interest_id not in target_interest_ids:
            db.delete(row)

    for interest_id in interest_ids:
        if interest_id in existing_interest_ids:
            continue
        db.add(ListingInterest(listing_id=listing_id, interest_id=interest_id))


def batch_listing_interest_ids(db: Session, listing_ids: list[UUID]) -> dict[UUID, list[UUID]]:
    if not listing_ids:
        return {}

    rows = db.exec(
        select(ListingInterest.listing_id, ListingInterest.interest_id).where(
            ListingInterest.__table__.c.listing_id.in_(listing_ids)
        )
    ).all()
    interest_map: dict[UUID, list[UUID]] = {listing_id: [] for listing_id in listing_ids}
    for row in rows:
        interest_map[row.listing_id].append(row.interest_id)
    return interest_map


def serialize_listing(
    listing: Listing,
    review_stats: dict | None = None,
    interest_ids: list[UUID] | None = None,
) -> dict:
    data = listing.model_dump(exclude={"embedding", "location"})
    if data.get("status") == Statuses.approved:
        data["status"] = Statuses.active

    location = listing.location
    data["location"] = extract_lat_lng(location)

    data["business_type_name"] = (
        listing.business_type_rel.name if listing.business_type_rel else None
    )
    data["business_name"] = (
        listing.business_rel.business_name if listing.business_rel else None
    )

    if review_stats is not None:
        data["avg_rating"] = review_stats.get("avg_rating")
        data["review_count"] = review_stats.get("review_count")

    data["interest_ids"] = interest_ids or []

    return data


def serialize_listings(db: Session, listings: list[Listing]) -> list[dict]:
    if not listings:
        return []
    listing_ids = [listing.id for listing in listings]
    stats_map = batch_review_stats(db, listing_ids)
    interest_map = batch_listing_interest_ids(db, listing_ids)
    return [
        serialize_listing(
            listing,
            stats_map[listing.id],
            interest_map.get(listing.id, []),
        )
        for listing in listings
    ]


def fetch_active_listings(db: Session, limit: int) -> list[Listing]:
    listings = db.exec(
        select(Listing)
        .where(Listing.status.in_(ACTIVE_LIKE_STATUSES))
        .options(
            selectinload(Listing.business_type_rel),
            selectinload(Listing.business_rel),
        )
        .limit(limit)
    ).all()
    random.shuffle(listings)
    return listings


def get_listing_review_stats(db: Session, listing_id) -> dict:
    return batch_review_stats(db, [listing_id])[listing_id]


def list_listings(
    db: Session,
    skip: int = 0,
    limit: int | None = None,
    city: str | None = None,
    country: str | None = None,
    business_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    status: str | None = None,
):
    query = select(Listing)

    if city:
        query = query.where(Listing.address["city"].astext.ilike(f"%{city}%"))
    if country:
        query = query.where(Listing.address["country"].astext.ilike(f"%{country}%"))
    if business_type:
        query = query.where(Listing.business_type == business_type)
    if min_price is not None:
        query = query.where(Listing.base_price >= min_price)
    if max_price is not None:
        query = query.where(Listing.base_price <= max_price)
    if status == Statuses.active.value or status == Statuses.approved.value:
        query = query.where(Listing.status.in_(ACTIVE_LIKE_STATUSES))
    elif status:
        query = query.where(Listing.status == status)
    if sort_by:
        sort_column = getattr(Listing, sort_by, None)
        if sort_column is not None:
            query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))

    query = query.options(
        selectinload(Listing.business_type_rel),
        selectinload(Listing.business_rel),
    ).offset(skip)
    if limit is not None:
        query = query.limit(limit)
    listings = db.exec(query).all()
    return serialize_listings(db, listings)


def get_listing_by_id(db: Session, listing_id: str):
    listing = db.exec(
        select(Listing)
        .where(Listing.id == listing_id)
        .options(
            selectinload(Listing.business_type_rel),
            selectinload(Listing.business_rel),
        )
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    review_stats = get_listing_review_stats(db, listing_id)
    interest_map = batch_listing_interest_ids(db, [listing.id])
    return serialize_listing(listing, review_stats, interest_map.get(listing.id, []))


def create_listing(db: Session, data: ListingCreate, user_id: str):
    validated_interest_ids = validate_interest_ids_for_business_type(
        db,
        data.business_type,
        data.interest_ids,
    )
    listing = Listing(
        **data.model_dump(exclude={"location", "interest_ids"})
    )

    if data.location:
        listing.location = build_location(data.location)

    db.add(listing)
    db.flush()
    sync_listing_interests(db, listing.id, validated_interest_ids)
    db.commit()
    db.refresh(listing)

    review_stats = get_listing_review_stats(db, listing.id)
    return serialize_listing(listing, review_stats, validated_interest_ids)


def update_listing(
    db: Session,
    listing_id: str,
    update_data: dict,
    user_id: str,
    is_admin: bool = False,
):
    listing = get_listing_or_404(db, listing_id)
    if not is_admin:
        business = get_business_by_user_id(db, user_id)
        if not business:
            raise HTTPException(status_code=403, detail="Not authorized")
        ensure_listing_belongs_to_business(
            listing,
            business,
            detail="Not authorized",
        )
        if listing.status == Statuses.suspended:
            raise HTTPException(
                status_code=403,
                detail="Suspended listings can only be updated by an admin",
            )
        requested_status = update_data.get("status")
        if requested_status is not None and requested_status != listing.status:
            allowed_owner_transitions = {
                (Statuses.active, Statuses.inactive),
                (Statuses.inactive, Statuses.active),
            }
            if (listing.status, requested_status) not in allowed_owner_transitions:
                raise HTTPException(
                    status_code=403,
                    detail="Business owners can only archive or restore their listings",
                )

    should_update_interests = "interest_ids" in update_data
    requested_interest_ids = update_data.pop("interest_ids", None)
    next_business_type = update_data.get("business_type", listing.business_type)
    validated_interest_ids = (
        validate_interest_ids_for_business_type(
            db,
            next_business_type,
            requested_interest_ids,
        )
        if should_update_interests
        else None
    )

    if "location" in update_data:
        listing.location = build_location(update_data.pop("location"))

    for key, value in update_data.items():
        setattr(listing, key, value)

    if should_update_interests and validated_interest_ids is not None:
        sync_listing_interests(db, listing.id, validated_interest_ids)

    db.commit()
    db.refresh(listing)
    review_stats = get_listing_review_stats(db, listing.id)
    interest_map = batch_listing_interest_ids(db, [listing.id])
    return serialize_listing(listing, review_stats, interest_map.get(listing.id, []))


def delete_listing(db: Session,listing: Listing):

    listing.status = Statuses.deleted
    listing.updated_at = func.now()

    db.commit()
    db.refresh(listing)
    return listing



def get_active_listings(db: Session, limit: int = 20):
    return serialize_listings(db, fetch_active_listings(db, limit))


def get_business_listings(db: Session, user_id: str):
    business = get_business_by_user_id(db, user_id)
    if not business:
        return []
    listings = db.exec(
        select(Listing)
        .where(Listing.business_id == business.id)
        .options(
            selectinload(Listing.business_type_rel),
            selectinload(Listing.business_rel),
        )
        .order_by(desc(Listing.created_at))
    ).all()
    return serialize_listings(db, listings)


def get_personalized_listings(db: Session, user_id: str, limit: int = 20):
    user_interests = list(
        db.exec(select(UserInterest.interest_id).where(UserInterest.user_id == user_id)).all()
    )

    if not user_interests:
        return serialize_listings(db, fetch_active_listings(db, limit))

    try:
        # PostgreSQL doesn't allow ORDER BY random() with DISTINCT unless random() is in SELECT
        # So we fetch listing IDs first, then fetch the listings
        listing_ids_subq = (
            select(ListingInterest.listing_id)
            .join(Listing, Listing.id == ListingInterest.listing_id)
            .where(ListingInterest.__table__.c.interest_id.in_(user_interests))
            .where(Listing.status.in_(ACTIVE_LIKE_STATUSES))
            .options(
                selectinload(Listing.business_type_rel),
                selectinload(Listing.business_rel),
            )
            .distinct()
        )

        # Get IDs with random ordering using a subquery approach
        ids_with_random = db.exec(
            select(Listing.id, func.random().label('rand'))
            .join(ListingInterest, ListingInterest.listing_id == Listing.id)
            .where(ListingInterest.__table__.c.interest_id.in_(user_interests))
            .where(Listing.status.in_(ACTIVE_LIKE_STATUSES))
            .options(
                selectinload(Listing.business_type_rel),
                selectinload(Listing.business_rel),
            )
            .distinct()
            .limit(limit)
            .order_by(func.random())
        ).all()

        if ids_with_random:
            # Sort by random value and pick limit
            shuffled = sorted(ids_with_random, key=lambda x: x.rand)[:limit]
            listing_ids = [row.id for row in shuffled]
            listings = db.exec(
                select(Listing)
                .where(Listing.id.in_(listing_ids))
                .where(Listing.status == Statuses.active)
            ).all()
        else:
            listings = fetch_active_listings(db, limit)

        if not listings:
            listings = fetch_active_listings(db, limit)

        return serialize_listings(db, listings)
    except Exception:
        return serialize_listings(db, fetch_active_listings(db, limit))


def search_listings_combined(
    db: Session,
    q: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float = 25,
    limit: int = 20,
):
    query = (
        select(Listing)
        .where(Listing.status.in_(ACTIVE_LIKE_STATUSES))
        .options(
            selectinload(Listing.business_type_rel),
            selectinload(Listing.business_rel),
        )
    )

    ts_vector = func.to_tsvector(
        "english",
        func.concat_ws(" ", Listing.title, func.coalesce(Listing.description, "")),
    )
    rank_expr = None
    if q:
        ts_query = func.plainto_tsquery("english", q)
        rank_expr = func.ts_rank(ts_vector, ts_query).label("rank")
        query = query.add_columns(rank_expr).where(ts_vector.op("@@")(ts_query))

    distance_expr = None
    if lat is not None and lng is not None:
        point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)

        distance_expr = func.ST_Distance(Listing.location, point).label("distance_m")

        query = query.add_columns(distance_expr).where(
            func.ST_DWithin(Listing.location, point, radius_km * 1000)
        )

    if rank_expr is not None:
        query = query.order_by(desc(rank_expr))
    elif distance_expr is not None:
        query = query.order_by(asc(distance_expr))
    else:
        query = query.order_by(desc(Listing.created_at))

    rows = db.exec(query.limit(limit)).all()

    if not rows:
        return []

    listings = [
        row[0] if isinstance(row, tuple) else row
        for row in rows
    ]

    serialized = serialize_listings(db, listings)
    listing_data_by_id = {item["id"]: item for item in serialized}

    for row in rows:
        listing = row[0] if isinstance(row, tuple) else row
        payload = listing_data_by_id.get(str(listing.id))
        if not payload:
            continue
        idx = 1
        if rank_expr is not None and len(row) > idx:
            rank_val = row[idx]
            payload["rank"] = float(rank_val) if rank_val is not None else None
            idx += 1
        if distance_expr is not None and len(row) > idx:
            dist_val = row[idx]
            payload["distance_m"] = float(dist_val) if dist_val is not None else None

    return serialized

def filter_by_availability(
    db: Session,
    listings: list[Listing],
    start_dt: datetime,
    end_dt: datetime,
    requested_quantity: int = 1,
) -> list[Listing]:
    """
    Returns only listings that have at least one service with available slots
    in the requested window. Uses a single batched query.
    """
    listing_ids = [l.id for l in listings]
    if not listing_ids:
        return []

    # Fetch all active services for these listings
    services = db.exec(
        select(Service)
        .where(col(Service.listing_id).in_(listing_ids))
        .where(Service.status == ServiceStatusTypes.active)
        .where(Service.capacity > 0)
    ).all()

    if not services:
        return []

    service_ids = [s.service_id for s in services]

    booked_rows = db.exec(
        select(Booking.service_id, func.coalesce(func.sum(Booking.amount_of_people), 0))
        .where(col(Booking.service_id).in_(service_ids))
        .where(col(Booking.status).notin_([
            BookingStatus.cancelled,
            BookingStatus.pending,
        ]))
        .where(Booking.booking_from_time < end_dt)
        .where(Booking.booking_to_time > start_dt)
        .group_by(Booking.service_id)
    ).all()

    booked_map = {service_id: int(booked or 0) for service_id, booked in booked_rows}

    # Determine which listing_ids have at least one available service
    available_listing_ids = set()
    for service in services:
        booked = booked_map.get(service.service_id, 0)
        if (service.capacity or 0) - booked >= requested_quantity:
            available_listing_ids.add(service.listing_id)

    return [l for l in listings if l.id in available_listing_ids]

