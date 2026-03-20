"""
Businesses API - Business management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlmodel import Session

from app.api.dependencies.auth import get_current_user_id
from app.database.session import get_db
from app.models.business_types import BusinessType
from app.schemas.business import BusinessCreate, BusinessUpdate
from app.services.business_service import list_businesses, get_business_by_id, create_business, update_business
from app.services.listing_service import get_business_listings as get_business_listings_service
from sqlmodel import select



router = APIRouter(prefix="/api/businesses", tags=["Businesses"])


def _require_user_id(user_id: str | None):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.get("", response_model=List[dict])
def get_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    """Get all businesses."""
    return list_businesses(db, skip=skip, limit=limit, verified_only=verified_only)

@router.get("/listings", response_model=List[dict])
def get_business_listings(business_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Get all listings for a business."""
    _require_user_id(business_id)
    return get_business_listings_service(db, business_id)

@router.get("/types", response_model=List[dict])
def get_business_types(db: Session = Depends(get_db)):
    """Get all business types."""
    types = db.exec(select(BusinessType)).all()
    return [{"id": str(t.id), "name": t.name} for t in types]

@router.get("/{business_id}", response_model=dict)
def get_business(business_id: str, db: Session = Depends(get_db)):
    """Get a single business with type details."""
    return get_business_by_id(db, business_id)





@router.post("", response_model=dict, status_code=201)
def create_business_endpoint(
    business_data: BusinessCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Create a new business."""
    _require_user_id(user_id)
    data = business_data.dict(exclude_unset=True)
    return create_business(db, data, user_id)


@router.put("/{business_id}", response_model=dict)
def update_business_endpoint(
    business_id: str,
    business_data: BusinessUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update a business."""
    _require_user_id(user_id)
    update_data = {k: v for k, v in business_data.dict(exclude_unset=True).items() if v is not None}
    return update_business(db, business_id, update_data, user_id)
