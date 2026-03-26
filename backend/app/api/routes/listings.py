from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session

from app.api.dependencies.permissions import require_listing_owner, require_roles
from app.database.session import get_db
from app.models.listing import Listing
from app.models.user import User
from app.schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from app.services.listing_service import (
    list_listings,
    get_listing_by_id,
    create_listing,
    update_listing,
    delete_listing,
    get_personalized_listings,
)

router = APIRouter(prefix="/api/listings", tags=["Listings"])
def _require_user_id(user_id: str | None):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
@router.get("", response_model=List[ListingResponse])
def get_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    city: str | None = None,
    country: str | None = None,
    business_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return list_listings(
        db=db,
        skip=skip,
        limit=limit,
        city=city,
        country=country,
        business_type=business_type,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        status=status,
    )


@router.get("/personalized", response_model=List[ListingResponse])
def get_personalized_listings_endpoint(
    current_user: User = Depends(require_roles("user", "business", "admin")),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    _require_user_id(current_user.id)
    return get_personalized_listings(db, current_user.id, limit)

@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    return get_listing_by_id(db, listing_id)


@router.post("", response_model=ListingResponse, status_code=201)
def create_listing_endpoint(
    listing_data: ListingCreate,
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    _require_user_id(current_user.id)
    data = listing_data.dict(exclude_unset=True)
    return create_listing(db, data, current_user.id)

@router.put("/{listing_id}", response_model=dict)
def update_listing_endpoint(
    listing_id: str,
    listing_data: ListingUpdate,
    listing: Listing = Depends(require_listing_owner),
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    update_data = {k: v for k, v in listing_data.dict(exclude_unset=True).items() if v is not None}
    return update_listing(
        db,
        listing.id,
        update_data,
        current_user.id,
        is_admin=current_user.is_super_admin,
    )
@router.delete("/{listing_id}", status_code=204)
def delete_listing_endpoint(
    listing_id: str,
    listing: Listing = Depends(require_listing_owner),
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    delete_listing(
        db,
        listing.id,
        current_user.id,
        is_admin=current_user.is_super_admin,
    )
    return None
