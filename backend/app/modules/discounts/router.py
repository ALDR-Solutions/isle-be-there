from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles

from .models import Discount
from .schemas import DiscountCreate, DiscountResponse, DiscountUpdate, DiscountEligibilityResponse
from .service import (
    create_discount,
    update_discount,
    get_active_discounts,
    get_discount_by_id,
    check_package_discount_eligibility,
    calculate_discount_for_amount,
    get_itinerary_total_estimated_cost,
)

from app.modules.itineraries.models import Itinerary

router = APIRouter(prefix="/api/discounts", tags=["Discounts"])


@router.get("", response_model=List[DiscountResponse])
def get_discounts_endpoint(db: Session = Depends(get_db), discount_type: Optional[str] = None):
    # Public endpoint: list all active discounts
    return get_active_discounts(db, discount_type=discount_type)


@router.get("/{discount_id}", response_model=DiscountResponse)
def get_discount_endpoint(discount_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_roles("admin"))):
    return get_discount_by_id(db, discount_id)


@router.get("/{discount_id}/eligibility", response_model=DiscountEligibilityResponse)
def discount_eligibility_endpoint(
    discount_id: UUID,
    itinerary_id: UUID,
    db: Session = Depends(get_db),
):
    # Public endpoint: check if a given itinerary is eligible for the specified discount
    # Approach: determine eligibility for the itinerary against all discounts, then align with the requested one
    # Import here to avoid circular imports during module load
    eligibility = check_package_discount_eligibility(db, itinerary_id)  # dict with keys: eligible, discount, reason

    # Fetch the requested discount for the response object
    discount = db.get(Discount, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Discount not found")

    discount_for_response = discount
    eligible = False
    reason = None
    estimated_discount = None

    if eligibility.get("discount") is not None and str(eligibility["discount"].id) == str(discount_id):
        eligible = bool(eligibility.get("eligible", False))
        reason = eligibility.get("reason")
        discount_for_response = eligibility["discount"]
        # Compute estimated discount amount for the itinerary and discount
        itinerary = db.get(Itinerary, itinerary_id)
        price = get_itinerary_total_estimated_cost(itinerary) if itinerary else 0.0
        discount_percent = getattr(discount_for_response, "discount_percent", 0.0) or 0.0
        max_cap = getattr(discount_for_response, "max_discount_amount", None)
        estimated_discount = calculate_discount_for_amount(price, discount_percent, max_cap)
    else:
        # Return the requested discount, but mark as not eligible for this itinerary by default
        reason = eligibility.get("reason") or "Discount not eligible for this itinerary"
        discount_for_response = discount

    return DiscountEligibilityResponse(
        discount=discount_for_response,
        eligible=eligible,
        reason=reason,
        estimated_discount=estimated_discount,
    )


@router.post("", response_model=DiscountResponse, status_code=status.HTTP_201_CREATED)
def create_discount_endpoint(
    data: DiscountCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    return create_discount(db, data.model_dump())


@router.put("/{discount_id}", response_model=DiscountResponse)
def update_discount_endpoint(
    discount_id: UUID,
    data: DiscountUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    return update_discount(db, discount_id, data.model_dump(exclude_unset=True))


@router.delete("/{discount_id}", response_model=DiscountResponse)
def deactivate_discount_endpoint(
    discount_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    # Soft deactivate by setting is_active to False
    return update_discount(db, discount_id, {"is_active": False})
