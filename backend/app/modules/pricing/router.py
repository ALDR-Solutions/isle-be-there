from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles
from .models import PlatformPricingConfig
from .schemas import (
    ListingPriceResponse,
    PlatformPricingConfigResponse,
    PlatformPricingConfigCreate,
)
from .service import (
    get_listing_display_price,
    create_pricing_config,
    update_pricing_config,
)


router = APIRouter(prefix="/api/pricing", tags=["Pricing"])


@router.get("/listing/{listing_id}", response_model=ListingPriceResponse)
def get_listing_pricing(listing_id: UUID, db: Session = Depends(get_db)):
    """Public endpoint: get display price for a listing.
    No authentication required.
    """
    return get_listing_display_price(db, listing_id)


@router.get("/config", response_model=List[PlatformPricingConfigResponse])
def list_pricing_configs(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("admin")),
):
    """Admin endpoint: list all pricing configurations."""
    stmt = select(PlatformPricingConfig)
    results = db.exec(stmt).all()
    return results


@router.post("/config", response_model=PlatformPricingConfigResponse, status_code=201)
def create_pricing_config_endpoint(
    data: PlatformPricingConfigCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("admin")),
):
    payload = data.model_dump(exclude_unset=True)
    config = create_pricing_config(db, payload)
    return config


@router.put("/config/{config_id}", response_model=PlatformPricingConfigResponse)
def update_pricing_config_endpoint(
    config_id: UUID,
    data: PlatformPricingConfigCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles("admin")),
):
    payload = data.model_dump(exclude_unset=True)
    return update_pricing_config(db, config_id, payload)
