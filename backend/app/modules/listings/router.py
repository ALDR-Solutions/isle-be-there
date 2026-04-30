from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_listing_owner, require_roles

from .models import Listing
from .schemas import ListingCreate, ListingResponse, ListingUpdate
from .service import (
    create_listing,
    delete_listing,
    get_listing_by_id,
    get_personalized_listings,
    list_listings,
    search_listings_combined,
    update_listing,
)

router = APIRouter(prefix="/api/listings", tags=["Listings"])




@router.get("", response_model=List[ListingResponse])
def get_listings(
    skip: int = Query(0, ge=0),
    limit: int | None = Query(default=None, ge=1, le=100),
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
        limit=limit,
    )


@router.get("/personalized", response_model=List[ListingResponse])
def get_personalized_listings_endpoint(
    current_user: User = Depends(require_roles("regular", "business", "admin")),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_personalized_listings(db, current_user.id, limit)


@router.get("/search")
def search_listings(
    q: str | None = Query(default=None, min_length=1),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lng: float | None = Query(default=None, ge=-180, le=180),
    radius_km: float = Query(default=25, gt=0, le=200),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if (lat is None) != (lng is None):
        raise HTTPException(status_code=400, detail="Both lat and lng are required together")

    return search_listings_combined(
        db=db,
        q=q,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        limit=limit,
    )


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    return get_listing_by_id(db, listing_id)


@router.post("", response_model=ListingResponse, status_code=201)
def create_listing_endpoint(
    listing_data: ListingCreate,
    current_user: User = Depends(require_roles("business")),
    db: Session = Depends(get_db),
):
    
    return create_listing(db, listing_data, current_user.id)


@router.put("/{listing_id}", response_model=ListingResponse)
def update_listing_endpoint(
    listing_data: ListingUpdate,
    listing: Listing = Depends(require_listing_owner),
    db: Session = Depends(get_db),
):
    update_data = listing_data.model_dump(exclude_unset=True)

    return update_listing(db, listing, update_data)


@router.delete("/{listing_id}", status_code=204)
def delete_listing_endpoint(
    listing: Listing = Depends(require_listing_owner),
    db: Session = Depends(get_db),
):
    delete_listing(db,listing)
    return Response(status_code=204)
