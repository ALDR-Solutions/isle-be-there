from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.listings.service import get_business_listings as get_business_listings_service
from app.shared.dependencies.permissions import require_business_owner, require_roles

from .models import Business
from .schemas import BusinessCreate, BusinessUpdate, BusinessBase
from .service import (
    create_business,
    get_business_by_id,
    get_business_by_user_id,
    list_business_types,
    list_businesses,
    update_business,
)

router = APIRouter(prefix="/api/businesses", tags=["Businesses"])


def _require_user_id(user_id: str | None):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")


@router.get("", response_model=List[BusinessBase])
def get_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    return list_businesses(db, skip=skip, limit=limit, verified_only=verified_only)


@router.get("/me", response_model=BusinessBase)
def get_my_business(
    current_user=Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    business = get_business_by_user_id(db, current_user.id)
    if not business:
        raise HTTPException(status_code=404, detail="No business found for this user")
    return business.model_dump()


@router.get("/listings", response_model=List[dict])
def get_business_listings(
    current_user=Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    _require_user_id(current_user.id)
    return get_business_listings_service(db, current_user.id)


@router.get("/types", response_model=List[dict])
def get_business_types_route(db: Session = Depends(get_db)):
    types = list_business_types(db)
    return [{"id": str(item.id), "name": item.name} for item in types]


@router.get("/{business_id}", response_model=dict)
def get_business(business_id: str, db: Session = Depends(get_db)):
    return get_business_by_id(db, business_id)


@router.post("", response_model=dict, status_code=201)
def create_business_endpoint(
    business_data: BusinessCreate,
    current_user=Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    _require_user_id(current_user.id)
    data = business_data.model_dump(exclude_unset=True)
    return create_business(db, data, current_user.id)


@router.put("/{business_id}", response_model=dict)
def update_business_endpoint(
    business_data: BusinessUpdate,
    business: Business = Depends(require_business_owner),
    current_user=Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    update_data = {
        key: value
        for key, value in business_data.model_dump(exclude_unset=True).items()
        if value is not None
    }
    return update_business(
        db,
        business.id,
        update_data,
        current_user.id,
        is_admin=current_user.is_super_admin,
    )