"""Business logic for listings."""

import random

from fastapi import HTTPException
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from shapely.geometry import Point
from sqlmodel import Session, asc, desc, select

from app.modules.businesses.models import Business
from app.modules.interests.models import ListingInterest, UserInterest
from app.modules.listings.schemas import ListingCreate
from app.modules.reviews.models import Review

from .models import Listing, Statuses


def _build_location(location_data):
    if not location_data:
        return None

    try:
        if isinstance(location_data, dict):
            lat = float(location_data.get("lat"))
            lng = float(location_data.get("lng"))
        else:
            # Pydantic object
            lat = float(location_data.lat)
            lng = float(location_data.lng)

    except (AttributeError, TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid location payload")

    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="lat and lng are required")

    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise HTTPException(status_code=400, detail="Location coordinates are out of range")

    return from_shape(Point(lng, lat), srid=4326)


def _batch_review_stats(db: Session, listing_ids: list) -> dict:
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


def _serialize_listing(listing: Listing, review_stats: dict | None = None) -> dict:
    data = listing.model_dump(exclude={"embedding", "location"})

    location = listing.location
    if isinstance(location, WKBElement):
        point = to_shape(location)
        data["location"] = {"lat": point.y, "lng": point.x}
    else:
        data["location"] = None

    data["business_type_name"] = (
        listing.business_type_rel.name if listing.business_type_rel else None
    )

    if review_stats is not None:
        data["avg_rating"] = review_stats.get("avg_rating")
        data["review_count"] = review_stats.get("review_count")

    return data


def _serialize_listings(db: Session, listings: list[Listing]) -> list[dict]:
    if not listings:
        return []
    listing_ids = [listing.id for listing in listings]
    stats_map = _batch_review_stats(db, listing_ids)
    return [_serialize_listing(listing, stats_map[listing.id]) for listing in listings]


def _fetch_active_listings(db: Session, limit: int) -> list[Listing]:
    listings = db.exec(
        select(Listing)
        .where(Listing.status == Statuses.active)
        .order_by(Listing.created_at.desc())
        .limit(limit)
    ).all()
    return listings


def get_listing_review_stats(db: Session, listing_id) -> dict:
    return _batch_review_stats(db, [listing_id])[listing_id]


def list_listings(db: Session,limit: int = 20) -> list[dict]:
    query = select(Listing)

    listings = db.exec(query.limit(limit)).all()
    return _serialize_listings(db, listings)


def get_listing_by_id(db: Session, listing_id: str):
    listing = db.exec(
        select(Listing)
        .where(Listing.id == listing_id)
        .options(selectinload(Listing.business_type_rel))
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    review_stats = get_listing_review_stats(db, listing_id)
    return _serialize_listing(listing, review_stats)


def create_listing(db: Session, data: ListingCreate, user_id: str):
    listing = Listing(
        **data.model_dump()
    )

    if data.location:
        listing.location = _build_location(data.location)

    db.add(listing)
    db.commit()
    db.refresh(listing)

    review_stats = get_listing_review_stats(db, listing.id)
    return _serialize_listing(listing, review_stats)


def update_listing(db: Session, listing: Listing, update_data: dict):

    if "location" in update_data:
        listing.location = _build_location(update_data.pop("location"))

    for key, value in update_data.items():
        setattr(listing, key, value)

    db.commit()
    db.refresh(listing)
    review_stats = get_listing_review_stats(db, listing.id)
    return _serialize_listing(listing, review_stats)


def delete_listing(db: Session,listing: Listing):

    listing.status = Statuses.deleted
    listing.updated_at = func.now()

    db.commit()
    db.refresh(listing)
    return listing



def get_active_listings(db: Session, limit: int = 20):
    return _serialize_listings(db, _fetch_active_listings(db, limit))


def get_business_listings(db: Session, user_id: str):
    business = db.exec(select(Business).where(Business.user_id == user_id)).first()
    if not business:
        return []
    listings = db.exec(
        select(Listing).where(Listing.business_id == business.id).order_by(desc(Listing.created_at))
    ).all()
    return _serialize_listings(db, listings)


def get_personalized_listings(db: Session, user_id: str, limit: int = 20):
    user_interests = list(
        db.exec(select(UserInterest.interest_id).where(UserInterest.user_id == user_id)).all()
    )

    if not user_interests:
        return _serialize_listings(db, _fetch_active_listings(db, limit))

    try:
        listings = db.exec(
            select(Listing)
            .join(ListingInterest, ListingInterest.listing_id == Listing.id)
            .where(ListingInterest.__table__.c.interest_id.in_(user_interests))
            .where(Listing.status == Statuses.active)
            .distinct()
            .limit(limit)
            .order_by(func.random())
        ).all()

        if not listings:
            listings = _fetch_active_listings(db, limit)


        return _serialize_listings(db, listings)
    except Exception:
        return _serialize_listings(db, _fetch_active_listings(db, limit))


def search_listings_combined(
    db: Session,
    q: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: float = 25,
    limit: int = 20,
):
    query = select(Listing).where(Listing.status == Statuses.active)

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

    query = query.options(selectinload(Listing.business_type_rel))

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

    serialized = _serialize_listings(db, listings)
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
