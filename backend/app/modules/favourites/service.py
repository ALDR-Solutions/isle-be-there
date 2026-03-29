from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.listings.models import Listing
from app.modules.listings.service import _serialize_listings

from .models import Favourites


def list_favourites(db: Session, user_id):
    query = (
        select(Favourites, Listing)
        .join(Listing, Favourites.listing_id == Listing.id)
        .where(Favourites.user_id == user_id)
    )
    rows = db.exec(query).all()
    serialized_listings = _serialize_listings(db, [listing for _, listing in rows])
    listings_by_id = {listing["id"]: listing for listing in serialized_listings}
    return [
        {
            "id": favourite.id,
            "user_id": favourite.user_id,
            "listing_id": favourite.listing_id,
            "created_at": favourite.created_at,
            "listing": listings_by_id.get(favourite.listing_id),
        }
        for favourite, listing in rows
    ]


def add_favourite(db: Session, user_id, listing_id):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    existing = db.exec(
        select(Favourites).where(
            Favourites.user_id == user_id,
            Favourites.listing_id == listing_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already favourited")

    favourite = Favourites(user_id=user_id, listing_id=listing_id)
    db.add(favourite)
    db.commit()
    db.refresh(favourite)
    serialized_listing = _serialize_listings(db, [listing])[0]
    return {
        "id": favourite.id,
        "user_id": favourite.user_id,
        "listing_id": favourite.listing_id,
        "created_at": favourite.created_at,
        "listing": serialized_listing,
    }


def remove_favourite(db: Session, user_id, listing_id):
    favourite = db.exec(
        select(Favourites).where(
            Favourites.user_id == user_id,
            Favourites.listing_id == listing_id,
        )
    ).first()
    if not favourite:
        raise HTTPException(status_code=404, detail="Favourite not found")

    db.delete(favourite)
    db.commit()
