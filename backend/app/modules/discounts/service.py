from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, update
from sqlmodel import Session, select

from .models import Discount, DiscountType
from ..itineraries.models import Itinerary, ItineraryItem
from ..listings.models import Listing


def now_utc() -> datetime:
    return datetime.utcnow()


def normalize_fractional_percent(value: Optional[float]) -> float:
    """Support legacy whole-number percentages while storing/returning fractions."""
    if value is None:
        return 0.0
    numeric = float(value)
    if numeric > 1:
        numeric = numeric / 100.0
    return max(numeric, 0.0)


def get_itinerary_total_estimated_cost(itinerary: Itinerary) -> float:
    value = getattr(itinerary, "total_estimated_cost", None)
    if value is None:
        value = getattr(itinerary, "total_price", 0.0)
    return float(value or 0.0)


def resolve_itinerary(db: Session, itinerary_or_id: UUID | Itinerary) -> Itinerary:
    if isinstance(itinerary_or_id, Itinerary):
        return itinerary_or_id

    itinerary = db.get(Itinerary, itinerary_or_id)
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary


def get_active_discounts(
    db: Session,
    discount_type: Optional[str | DiscountType] = None,
) -> list[Discount]:
    """Retrieve active discounts that are valid right now."""
    now = now_utc()
    stmt = select(Discount).where(
        Discount.is_active == True,
        Discount.valid_from <= now,
        or_(Discount.valid_to == None, Discount.valid_to >= now),
    )

    if discount_type is not None:
        try:
            resolved_type = (
                discount_type
                if isinstance(discount_type, DiscountType)
                else DiscountType(discount_type)
            )
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid discount type") from None
        stmt = stmt.where(Discount.discount_type == resolved_type)

    return db.exec(stmt).all()


def get_discount_by_id(db: Session, discount_id: UUID) -> Discount:
    discount = db.get(Discount, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")
    return discount


def collect_itinerary_business_types(itinerary_id: UUID, db: Session) -> set[str]:
    """Return business type names present across the itinerary's listings."""
    business_types: set[str] = set()
    stmt_items = select(ItineraryItem).where(ItineraryItem.itinerary_id == itinerary_id)
    items = db.exec(stmt_items).all()
    for item in items:
        listing = getattr(item, "listing_rel", None) or getattr(item, "listing", None)
        if listing is None and getattr(item, "listing_id", None) is not None:
            listing = db.get(Listing, item.listing_id)
        if listing is None:
            continue

        business_type_rel = getattr(listing, "business_type_rel", None)
        business_type = getattr(listing, "business_type", None)
        business_type_name = getattr(business_type_rel, "name", None)
        if business_type_name is None:
            business_type_name = getattr(business_type, "name", None)
        if business_type_name:
            business_types.add(str(business_type_name))
    return business_types


def check_package_discount_eligibility(
    db: Session,
    itinerary_or_id: UUID | Itinerary,
) -> dict:
    """Check whether an itinerary qualifies for the current package discount."""
    itinerary = resolve_itinerary(db, itinerary_or_id)
    itinerary_id = itinerary.id

    discounts = get_active_discounts(db, discount_type=DiscountType.PACKAGE)
    business_types = collect_itinerary_business_types(itinerary_id, db)

    stmt_items = select(ItineraryItem).where(ItineraryItem.itinerary_id == itinerary_id)
    items = db.exec(stmt_items).all()
    total_services = len(items)
    total_cost = get_itinerary_total_estimated_cost(itinerary)

    for discount in discounts:
        required = getattr(discount, "required_business_types", []) or []
        required_set = {str(item) for item in required}
        if required_set and not required_set.issubset(business_types):
            continue

        min_services = getattr(discount, "min_services", None)
        if min_services is not None and total_services < min_services:
            continue

        min_total_cost = getattr(discount, "min_total_cost", None)
        if min_total_cost is not None and total_cost < float(min_total_cost):
            continue

        max_uses = getattr(discount, "max_uses", None)
        current_uses = int(getattr(discount, "current_uses", 0) or 0)
        if max_uses is not None and current_uses >= int(max_uses):
            continue

        return {"eligible": True, "discount": discount, "reason": None}

    return {"eligible": False, "discount": None, "reason": "No eligible package discount"}


def get_eligible_package_discount(
    db: Session,
    itinerary_or_id: UUID | Itinerary,
) -> Optional[Discount]:
    eligibility = check_package_discount_eligibility(db, itinerary_or_id)
    if not eligibility.get("eligible"):
        return None
    return eligibility.get("discount")


def apply_discount_to_itinerary(db: Session, itinerary_id: UUID, discount_id: UUID) -> Itinerary:
    eligibility = check_package_discount_eligibility(db, itinerary_id)
    if not eligibility.get("eligible"):
        raise HTTPException(
            status_code=400,
            detail=eligibility.get("reason", "Discount not eligible"),
        )

    discount = eligibility.get("discount")
    if discount is None or str(discount.id) != str(discount_id):
        raise HTTPException(status_code=400, detail="Discount not eligible")

    itinerary = resolve_itinerary(db, itinerary_id)
    price = get_itinerary_total_estimated_cost(itinerary)
    discount_percent = normalize_fractional_percent(getattr(discount, "discount_percent", 0.0))
    max_cap = getattr(discount, "max_discount_amount", None)

    itinerary.applied_discount_id = discount_id
    itinerary.discount_amount = calculate_discount_for_amount(price, discount_percent, max_cap)
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    return itinerary


def calculate_discount_for_amount(
    display_price: float,
    discount_percent: float,
    max_discount_amount: Optional[float],
) -> float:
    normalized_percent = normalize_fractional_percent(discount_percent)
    base = float(display_price or 0.0) * normalized_percent
    if max_discount_amount is not None:
        base = min(base, float(max_discount_amount))
    return round(max(base, 0.0), 2)


def create_discount(db: Session, data: dict) -> Discount:
    payload = dict(data)
    if "discount_percent" in payload and payload["discount_percent"] is not None:
        payload["discount_percent"] = normalize_fractional_percent(payload["discount_percent"])

    discount = Discount(**payload)
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount


def update_discount(db: Session, discount_id: UUID, data: dict) -> Discount:
    discount = db.get(Discount, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")

    payload = dict(data)
    if "discount_percent" in payload and payload["discount_percent"] is not None:
        payload["discount_percent"] = normalize_fractional_percent(payload["discount_percent"])

    for key, value in payload.items():
        setattr(discount, key, value)
    db.add(discount)
    db.commit()
    db.refresh(discount)
    return discount


def increment_discount_usage(db: Session, discount_id: UUID) -> Discount:
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
    discounts = get_active_discounts(db, discount_type=DiscountType.PACKAGE)
    if discounts:
        return discounts[0]

    return create_discount(
        db,
        {
            "name": "Package Discount",
            "discount_type": DiscountType.PACKAGE,
            "discount_percent": 0.10,
            "min_services": 2,
            "is_active": True,
            "valid_from": now_utc(),
        },
    )
