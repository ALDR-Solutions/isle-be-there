from datetime import date as date_class
from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.domain import get_listing_or_404
from app.shared.dependencies.permissions import require_listing_owner, require_roles

from .models import Listing
from .schemas import (
    ListingCreate,
    ListingModerationUpdate,
    ListingResponse,
    ListingUpdate,
)
from .service import (
    create_listing,
    delete_listing,
    get_cities_for_country,
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
    limit: int = Query(100, ge=1, le=100),
    city: str | None = Query(default=None),
    country: str | None = Query(default=None),
    business_type: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    sort_by: str | None = Query(default=None),
    sort_order: Literal["asc", "desc"] = Query(default="asc"),
    status: str | None = Query(default=None),
    availability_date: date_class | None = Query(default=None),
    city_lat: float | None = Query(default=None, ge=-90, le=90),
    city_lng: float | None = Query(default=None, ge=-180, le=180),
    radius_km: float | None = Query(default=None, gt=0),
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
        availability_date=availability_date,
        city_lat=city_lat,
        city_lng=city_lng,
        radius_km=radius_km,
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
        raise HTTPException(
            status_code=400, detail="Both lat and lng are required together"
        )

    return search_listings_combined(
        db=db,
        q=q,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        limit=limit,
    )


@router.get("/cities/{country}")
def get_cities_by_country(country: str, db: Session = Depends(get_db)):
    """Get cities with listings for a given country, with geo centers and radius options."""
    return get_cities_for_country(db, country)


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
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    update_data = listing_data.model_dump(exclude_unset=True)

    return update_listing(
        db,
        listing,
        update_data,
        is_admin=current_user.user_type == "admin",
    )


@router.patch("/{listing_id}/moderate", response_model=ListingResponse)
def moderate_listing_endpoint(
    listing_id: str,
    listing_data: ListingModerationUpdate,
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    listing = get_listing_or_404(db, listing_id)
    update_data = listing_data.model_dump()

    return update_listing(
        db,
        listing,
        update_data,
        is_admin=current_user.user_type == "admin",
    )


@router.delete("/{listing_id}", status_code=204)
def delete_listing_endpoint(
    listing: Listing = Depends(require_listing_owner),
    db: Session = Depends(get_db),
):
    delete_listing(db, listing)
    return Response(status_code=204)
