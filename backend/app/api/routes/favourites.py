from fastapi import APIRouter, Depends, HTTPException
from app.database.session import get_db
from sqlmodel import Session, select
from app.models.favourites import Favourites
from app.models.listing import Listing
from app.api.dependencies.permissions import get_current_user
from app.models.user import User
from app.schemas.favourites import FavouriteResponse
from app.services.listing_service import _serialize_listings
from uuid import UUID

router = APIRouter(prefix="/api/favourites", tags=["Favourites"])


@router.get("/", response_model=list[FavouriteResponse], include_in_schema=False)
@router.get("", response_model=list[FavouriteResponse])
def get_favourites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(Favourites, Listing)
        .join(Listing, Favourites.listing_id == Listing.id)
        .where(Favourites.user_id == current_user.id)
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


@router.post("/{listing_id}", response_model=FavouriteResponse)
def add_favourite(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Check for duplicate
    existing = db.exec(
        select(Favourites).where(
            Favourites.user_id == current_user.id,
            Favourites.listing_id == listing_id,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Already favourited")

    fav = Favourites(user_id=current_user.id, listing_id=listing_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    serialized_listing = _serialize_listings(db, [listing])[0]
    return {
        "id": fav.id,
        "user_id": fav.user_id,
        "listing_id": fav.listing_id,
        "created_at": fav.created_at,
        "listing": serialized_listing,
    }


@router.delete("/{listing_id}")
def remove_favourite(
    listing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fav = db.exec(
        select(Favourites).where(
            Favourites.user_id == current_user.id,
            Favourites.listing_id == listing_id,
        )
    ).first()

    if not fav:
        raise HTTPException(status_code=404, detail="Favourite not found")

    db.delete(fav)
    db.commit()
    return {"detail": "Removed"}
