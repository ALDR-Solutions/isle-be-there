"""Business logic for listings."""

import random

from fastapi import HTTPException
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy import func
from sqlalchemy.sql.functions import count
from sqlalchemy.orm import selectinload
from sqlmodel import Session, asc, desc, select

from app.modules.businesses.models import Business
from app.modules.interests.models import ListingInterest, UserInterest
from app.modules.reviews.models import Review
from app.modules.users.models import User

from .models import Listing, Statuses


def _batch_review_stats(db: Session, listing_ids: list) -> dict:
    if not listing_ids:
        return {}

    rows = db.exec(
        select(
            Review.listing_id,
            func.avg(Review.rating).label("avg_rating"),
            count(Review.id).label("review_count"),
        )
        .where(Review.__table__.c.listing_id.in_(listing_ids))
        .group_by(Review.listing_id)
    ).all()

    stats = {
        row.listing_id: {
            "avg_rating": float(row.avg_rating) if row.avg_rating is not None else None,
            "review_count": int(row.review_count),
        }
        for row in rows
    }

    for listing_id in listing_ids:
        stats.setdefault(listing_id, {"avg_rating": None, "review_count": 0})

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
        data.update(review_stats)

    return data


def _serialize_listings(db: Session, listings: list[Listing]) -> list[dict]:
    if not listings:
        return []
    listing_ids = [listing.id for listing in listings]
    stats_map = _batch_review_stats(db, listing_ids)
    return [_serialize_listing(listing, stats_map[listing.id]) for listing in listings]


def _fetch_active_listings(db: Session, limit: int) -> list[Listing]:
    listings = db.exec(select(Listing).where(Listing.status == Statuses.active).limit(limit)).all()
    random.shuffle(listings)
    return listings


def get_listing_review_stats(db: Session, listing_id) -> dict:
    stmt = select(
        func.avg(Review.rating).label("avg_rating"),
        count(Review.id).label("review_count"),
    ).where(Review.listing_id == listing_id)
    row = db.exec(stmt).one()
    return {
        "avg_rating": float(row.avg_rating) if row.avg_rating is not None else None,
        "review_count": int(row.review_count) if row.review_count is not None else 0,
    }


def list_listings(
    db: Session,
    skip: int = 0,
    limit: int = 20,
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
    if status:
        query = query.where(Listing.status == status)
    if sort_by:
        sort_column = getattr(Listing, sort_by, None)
        if sort_column is not None:
            query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))

    query = query.options(selectinload(Listing.business_type_rel))
    listings = db.exec(query.offset(skip).limit(limit)).all()
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


def create_listing(db: Session, data: dict, user_id: str):
    business = db.exec(select(Business).where(Business.user_id == user_id)).first()
    if not business:
        raise HTTPException(status_code=400, detail="User does not have a business")
    data["business_id"] = business.id
    listing = Listing(**data)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    review_stats = get_listing_review_stats(db, listing.id)
    return _serialize_listing(listing, review_stats)


def update_listing(
    db: Session,
    listing_id: str,
    update_data: dict,
    user_id: str,
    is_admin: bool = False,
):
    listing = db.exec(select(Listing).where(Listing.id == listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not is_admin:
        business = db.exec(select(Business).where(Business.user_id == user_id)).first()
        if not business or str(listing.business_id) != str(business.id):
            raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in update_data.items():
        setattr(listing, key, value)
    db.commit()
    db.refresh(listing)
    review_stats = get_listing_review_stats(db, listing.id)
    return _serialize_listing(listing, review_stats)


def delete_listing(
    db: Session,
    listing_id: str,
    user_id: str,
    is_admin: bool = False,
):
    listing = db.exec(select(Listing).where(Listing.id == listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not is_admin:
        business = db.exec(select(Business).where(Business.user_id == user_id)).first()
        if not business or str(listing.business_id) != str(business.id):
            raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(listing)
    db.commit()


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
        ).all()

        if not listings:
            listings = _fetch_active_listings(db, limit)
        else:
            random.shuffle(listings)

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
        point = f"SRID=4326;POINT({lng} {lat})"
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

    if isinstance(rows[0], Listing):
        return _serialize_listings(db, rows)

    listings = [row[0] for row in rows]
    serialized = _serialize_listings(db, listings)
    listing_data_by_id = {item["id"]: item for item in serialized}

    for row in rows:
        listing = row[0]
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
