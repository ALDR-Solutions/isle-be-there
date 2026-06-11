from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy import or_

from app.modules.pricing.models import PlatformPricingConfig
from app.modules.listings.models import Listing
from app.modules.services.service import get_service_by_id  # reference pattern


def now_utc() -> datetime:
    # helper to centralize time source if needed later
    return datetime.utcnow()


def query_active_config(db: Session, business_type_id: Optional[UUID]) -> Optional[PlatformPricingConfig]:
    now = now_utc()
    # Active config for a specific business_type_id
    stmt = select(PlatformPricingConfig).where(
        PlatformPricingConfig.is_active == True,
        PlatformPricingConfig.effective_from <= now,
        or_(PlatformPricingConfig.effective_to == None, PlatformPricingConfig.effective_to >= now),
        PlatformPricingConfig.business_type_id == business_type_id,
    )
    res = db.exec(stmt).first()
    if res:
        return res
    return None


def get_pricing_config(db: Session, business_type_id: Optional[UUID] = None) -> PlatformPricingConfig:
    """Get active pricing config for a given business_type_id or global (None).

    Raises HTTPException 404 if no active config is found.
    """
    # Try specific business type first (if provided)
    if business_type_id is not None:
        config = query_active_config(db, business_type_id)
        if config is not None:
            return config
    # Fallback to global (None) config
    global_config = query_active_config(db, None)
    if global_config is not None:
        return global_config
    raise HTTPException(status_code=404, detail="Pricing config not found")


def calculate_display_price(db: Session, listing_id: UUID, service_id: Optional[UUID] = None) -> dict:
    """Calculate display price for a listing (and optional service).

    Returns dict with: base_price, service_fee_percent, service_fee_amount, display_price
    """
    # Resolve base price: prefer service.price if provided, otherwise listing.base_price
    listing = db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    base_price: Optional[float] = None
    if service_id is not None:
        service = get_service_by_id(db, service_id)
        if getattr(service, "price", None) is not None:
            base_price = service.price
    if base_price is None:
        base_price = listing.base_price
    if base_price is None:
        # As per requirements, raise 400 when listing has no base price
        raise HTTPException(status_code=400, detail="Listing has no base price set")

    # Determine pricing config: try listing's business_type first, then global; default to 0.10 if none
    config = None
    if getattr(listing, "business_type_id", None) is not None:
        try:
            config = get_pricing_config(db, listing.business_type_id)  # may raise 404
        except HTTPException:
            config = None
    if config is None:
        try:
            config = get_pricing_config(db, None)
        except HTTPException:
            config = None

    service_fee_percent = getattr(config, "service_fee_percent", None) if config else None
    if service_fee_percent is None:
        service_fee_percent = 0.10  # default 10%

    service_fee_amount = float(base_price) * float(service_fee_percent)
    display_price = float(base_price) + service_fee_amount

    return {
        "base_price": base_price,
        "service_fee_percent": float(service_fee_percent),
        "service_fee_amount": service_fee_amount,
        "display_price": display_price,
    }


def get_listing_display_price(db: Session, listing_id: UUID) -> dict:
    """Wrapper to get display price for a listing using only listing_id."""
    result = calculate_display_price(db, listing_id)
    result["listing_id"] = listing_id
    return result


def create_pricing_config(db: Session, data: dict) -> PlatformPricingConfig:
    """Create new PlatformPricingConfig from provided data."""
    config = PlatformPricingConfig(**data)  # type: ignore[arg-type]
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def update_pricing_config(db: Session, config_id: UUID, data: dict) -> PlatformPricingConfig:
    """Update existing PlatformPricingConfig by id."""
    config = db.get(PlatformPricingConfig, config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="Pricing config not found")
    for key, value in data.items():
        setattr(config, key, value)
    db.add(config)
    db.commit()
    db.refresh(config)
    return config
