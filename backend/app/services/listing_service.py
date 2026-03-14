"""Business logic for listings."""

from fastapi import HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.listing import Listing


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
):
    query = db.query(Listing)

    if city:
        query = query.filter(Listing.address["city"].astext.ilike(f"%{city}%"))
    if country:
        query = query.filter(Listing.address["country"].astext.ilike(f"%{country}%"))
    if business_type:
        query = query.filter(Listing.business_type == business_type)
    if min_price is not None:
        query = query.filter(Listing.base_price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.base_price <= max_price)

    if sort_by:
        sort_column = getattr(Listing, sort_by, None)
        if sort_column is not None:
            query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))

    listings = query.offset(skip).limit(limit).all()
    return [listing.model_dump() for listing in listings]


def get_listing_by_id(db: Session, listing_id: str):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing.model_dump()


def create_listing(db: Session, data: dict, user_id: str):
    data["business_id"] = user_id
    listing = Listing(**data)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing.model_dump()


def update_listing(db: Session, listing_id: str, update_data: dict, user_id: str):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if str(listing.business_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in update_data.items():
        setattr(listing, key, value)
    db.commit()
    db.refresh(listing)
    return listing.model_dump()


def delete_listing(db: Session, listing_id: str, user_id: str):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if str(listing.business_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(listing)
    db.commit()
