from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session

from app.api.dependencies.auth import get_current_user_id
from app.database.session import get_db
from app.schemas.listing import ListingCreate, ListingUpdate
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
@router.get("", response_model=List[dict])
def get_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    city: str | None = None,
    country: str | None = None,
    business_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str | None = None,
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
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


@router.get("/personalized", response_model=List[dict])
def get_personalized_listings_endpoint(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    return get_personalized_listings(db, user_id, limit)

@router.get("/{listing_id}", response_model=dict)
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    return get_listing_by_id(db, listing_id)


@router.post("", response_model=dict, status_code=201)
def create_listing_endpoint(
    listing_data: ListingCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    data = listing_data.dict(exclude_unset=True)
    return create_listing(db, data, user_id)
@router.put("/{listing_id}", response_model=dict)
def update_listing_endpoint(
    listing_id: str,
    listing_data: ListingUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    update_data = {k: v for k, v in listing_data.dict(exclude_unset=True).items() if v is not None}
    return update_listing(db, listing_id, update_data, user_id)
@router.delete("/{listing_id}", status_code=204)
def delete_listing_endpoint(
    listing_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    _require_user_id(user_id)
    delete_listing(db, listing_id, user_id)
    return None

