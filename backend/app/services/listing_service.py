"""Business logic for listings."""

import random
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from fastapi import HTTPException
from sqlmodel import asc, desc, Session, select

from app.models.listing import Listing, Statuses
from app.models.user_interest import UserInterest
from app.models.listing_interest import ListingInterest
from app.models.business import Business
from app.models.review import Review
from app.models.user import User
from sqlalchemy import func
from sqlalchemy.sql.functions import count


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _batch_review_stats(db: Session, listing_ids: list) -> dict:
    """Fetch avg_rating and review_count for multiple listings in one query.
    
    Returns:
        dict: { listing_id: { "avg_rating": float | None, "review_count": int } }
    """
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

    # Listings with no reviews won't appear in the result — fill defaults
    for listing_id in listing_ids:
        stats.setdefault(listing_id, {"avg_rating": None, "review_count": 0})

    return stats


def _serialize_listing(listing: Listing, review_stats: dict | None = None) -> dict:
    """Convert a Listing ORM object to a JSON-safe dict, optionally with review stats.
    
    Args:
        listing: The ORM listing object.
        review_stats: Pre-fetched { "avg_rating": ..., "review_count": ... }.
                      If None, stats are fetched individually (use only for single listings).
    """
    data = listing.model_dump(exclude={"embedding", "location"})

    location = listing.location
    if isinstance(location, WKBElement):
        point = to_shape(location)
        data["location"] = {"lat": point.y, "lng": point.x}
    else:
        data["location"] = location

    if review_stats is not None:
        data.update(review_stats)

    return data


def _serialize_listings(db: Session, listings: list[Listing]) -> list[dict]:
    """Serialize a list of listings with batched review stats (no N+1)."""
    if not listings:
        return []
    listing_ids = [listing.id for listing in listings]
    stats_map = _batch_review_stats(db, listing_ids)
    return [_serialize_listing(listing, stats_map[listing.id]) for listing in listings]


def _fetch_active_listings(db: Session, limit: int) -> list[Listing]:
    listings = db.exec(
        select(Listing).where(Listing.status == Statuses.active).limit(limit)
    ).all()
    random.shuffle(listings)
    return listings


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def get_listing_review_stats(db: Session, listing_id) -> dict:
    """Single-listing review stats. Prefer _batch_review_stats for lists."""
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

    listings = db.exec(query.offset(skip).limit(limit)).all()
    return _serialize_listings(db, listings)


def get_listing_by_id(db: Session, listing_id: str):
    listing = db.exec(select(Listing).where(Listing.id == listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    review_stats = get_listing_review_stats(db, listing_id)
    return _serialize_listing(listing, review_stats)


def create_listing(db: Session, data: dict, user_id: str):
    business = db.exec(select(Business).where(Business.user_id == user_id)).first()
    if not business:
        user = db.exec(select(User).where(User.id == user_id)).first()
        business_name = user.username or user.email.split("@")[0] if user else "My Business"
        business = Business(user_id=user_id, business_name=business_name)
        db.add(business)
        db.commit()
        db.refresh(business)
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
        select(Listing)
        .where(Listing.business_id == business.id)
        .order_by(desc(Listing.created_at))
    ).all()
    return _serialize_listings(db, listings)


def get_personalized_listings(db: Session, user_id: str, limit: int = 20):
    """Personalize listings based on user interests, falling back to active listings."""
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

    except Exception as e:
        print("Error personalizing listings:", e)
        return _serialize_listings(db, _fetch_active_listings(db, limit))
