from __future__ import annotations

from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select
from sqlalchemy import update
from fastapi import HTTPException

from .models import Discount, DiscountType
from ..itineraries.models import Itinerary, ItineraryItem
from ..listings.models import Listing


def get_active_discounts(db: Session, discount_type: Optional[str | DiscountType] = None) -> List[Discount]:
    """
    Retrieve all active discounts, optionally filtered by type.
    - Considers date window if fields exist (start_date, end_date)
    - Applies type filter if provided
    - Considers active/is_active flags if present
    """
    now = datetime.utcnow()
    stmt = select(Discount)

    # Date validity window
    if hasattr(Discount, "start_date"):
        stmt = stmt.where(Discount.start_date <= now)
    if hasattr(Discount, "end_date"):
        stmt = stmt.where(Discount.end_date >= now)

    # Type filtering
    if discount_type is not None:
        try:
            dtype = DiscountType(discount_type) if not isinstance(discount_type, DiscountType) else discount_type
        except (TypeError, ValueError):
            dtype = discount_type  # Fallback to raw value
        if hasattr(Discount, "type"):
            stmt = stmt.where(Discount.type == dtype)

    # Active flags if present
    if hasattr(Discount, "active"):
        stmt = stmt.where(Discount.active == True)
    if hasattr(Discount, "is_active"):
        stmt = stmt.where(Discount.is_active == True)

    results = db.exec(stmt).all()
    return results


def get_discount_by_id(db: Session, discount_id: UUID) -> Discount:
    discount = db.get(Discount, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    return discount


def collect_itinerary_business_types(itinerary_id: UUID, db: Session) -> set[str]:
    """Return a set of business_type names found in the itinerary's listings."""
    business_types: set[str] = set()
    stmt_items = select(ItineraryItem).where(ItineraryItem.itinerary_id == itinerary_id)
    items = db.exec(stmt_items).scalars().all()
    for item in items:
        listing = getattr(item, "listing", None)
        if listing is None:
            listing_id = getattr(item, "listing_id", None)
            if listing_id is not None:
                listing = db.get(Listing, listing_id)
        if listing is None:
            continue
        bt_name = None
        if hasattr(listing, "business_type_rel") and listing.business_type_rel is not None:
            bt_name = getattr(listing.business_type_rel, "name", None)
        if not bt_name and hasattr(listing, "business_type") and listing.business_type is not None:
            bt_name = getattr(listing.business_type, "name", None)
        if bt_name:
            business_types.add(str(bt_name))
    return business_types


def check_package_discount_eligibility(db: Session, itinerary_id: UUID) -> Dict:
    """Check if itinerary qualifies for a package discount.
    Returns: {eligible: bool, discount: Discount | None, reason: str | None}
    """
    itinerary = db.get(Itinerary, itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    # Fetch possible package discounts
    pkg_type = getattr(DiscountType, "PACKAGE", None)
    discounts = get_active_discounts(db, discount_type=pkg_type)

    business_types = collect_itinerary_business_types(itinerary_id, db)

    # Count services in itinerary
    stmt_items = select(ItineraryItem).where(ItineraryItem.itinerary_id == itinerary_id)
    items = db.exec(stmt_items).scalars().all()
    total_services = len(items)

    price = getattr(itinerary, "total_price", 0.0) or 0.0

    now = datetime.utcnow()

    for discount in discounts:
        # Required business types
        required = getattr(discount, "required_business_types", []) or []
        required_set = set(str(t) for t in required)
        if required_set and not required_set.issubset(business_types):
            continue

        # Min services
        min_services = getattr(discount, "min_services", None)
        if min_services is not None and total_services < min_services:
            continue

        # Min total cost
        min_total = getattr(discount, "min_total_cost", None)
        if min_total is not None and price < min_total:
            continue

        # Date window
        start = getattr(discount, "start_date", None)
        end = getattr(discount, "end_date", None)
        if start and now < start:
            continue
        if end and now > end:
            continue

        # Usage limit
        max_uses = getattr(discount, "max_uses", None)
        current_uses = getattr(discount, "current_uses", 0)
        if max_uses is not None and current_uses >= max_uses:
            continue

        # Active flag
        if hasattr(discount, "active") and not discount.active:
            continue
        if hasattr(discount, "is_active") and not discount.is_active:
            continue

        return {"eligible": True, "discount": discount, "reason": None}

    return {"eligible": False, "discount": None, "reason": "No eligible package discount"}


def apply_discount_to_itinerary(db: Session, itinerary_id: UUID, discount_id: UUID) -> Itinerary:
    eligibility = check_package_discount_eligibility(db, itinerary_id)
    if not eligibility.get("eligible"):
        raise HTTPException(status_code=400, detail=eligibility.get("reason", "Discount not eligible"))
    discount = eligibility.get("discount")
    if discount is None:
        raise HTTPException(status_code=404, detail="Discount not found")

    itinerary = db.get(Itinerary, itinerary_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    price = getattr(itinerary, "total_price", 0.0) or 0.0
    discount_percent = getattr(discount, "discount_percent", 0.0) or 0.0
    max_cap = getattr(discount, "max_discount_amount", None)

    amount = calculate_discount_for_amount(price, discount_percent, max_cap)

    itinerary.applied_discount_id = discount_id
    itinerary.discount_amount = amount
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    return itinerary


def calculate_discount_for_amount(display_price: float, discount_percent: float, max_discount_amount: Optional[float]) -> float:
    base = display_price * (discount_percent / 100.0)
    if max_discount_amount is not None:
        base = min(base, max_discount_amount)
    if base < 0:
        base = 0.0
    return round(base, 2)


def create_discount(db: Session, data: dict) -> Discount:
    discount = Discount(**data)
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount


def update_discount(db: Session, discount_id: UUID, data: dict) -> Discount:
    discount = db.get(Discount, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    for k, v in data.items():
        setattr(discount, k, v)
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount


def increment_discount_usage(db: Session, discount_id: UUID) -> Discount:
    # Atomic increment with race-condition protection
    result = db.exec(
        update(Discount)
        .where(Discount.id == discount_id)
        .where((Discount.current_uses < Discount.max_uses) | (Discount.max_uses.is_(None)))
        .values(current_uses=Discount.current_uses + 1)
    )
    if getattr(result, "rowcount", 0) == 0:
        raise HTTPException(400, "Discount usage limit exceeded")
    return db.get(Discount, discount_id)


def get_or_create_package_discount(db: Session) -> Discount:
    """Return an active PACKAGE discount, creating a default one if none exists.

    - Attempts to fetch an active package discount via get_active_discounts(db, discount_type=DiscountType.PACKAGE).
    - If found, returns the first active package discount.
    - If none exists, creates a default package discount with sane defaults and returns it.
    """
    # Try to fetch an existing active package discount
    discounts = get_active_discounts(db, discount_type=DiscountType.PACKAGE)
    if discounts:
        return discounts[0]

    # No active package discount found; create a default one
    data = {
        "name": "Package Discount",
        "discount_type": DiscountType.PACKAGE,
        "discount_percent": 10.0,  # 10%
        "min_services": 2,
        "is_active": True,
        "valid_from": datetime.utcnow(),
        # valid_to intentionally left as None (no expiry)
    }
    return create_discount(db, data)
