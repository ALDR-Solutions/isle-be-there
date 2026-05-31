from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.modules.businesses.models import Business
from app.modules.employees.models import Business_Employee
from app.modules.itineraries.models import Itinerary
from app.modules.listings.models import Listing

from .lookups import (
    get_business_by_user_id,
    get_itinerary_item_or_404,
    get_listing_or_404,
)
from .ownership import ensure_itinerary_owner


def get_owned_business_or_404(
    db: Session,
    owner_id: UUID | str,
    detail: str = "Business not found for this user",
) -> Business:
    business = get_business_by_user_id(db, owner_id)
    if business is None:
        raise HTTPException(status_code=404, detail=detail)
    return business


def get_business_employee_link_or_404(
    db: Session,
    business_id: UUID | str,
    employee_id: UUID | str,
    detail: str = "Employee not found for this business",
) -> Business_Employee:
    employee_link = db.exec(
        select(Business_Employee).where(
            Business_Employee.business_id == business_id,
            Business_Employee.employee_id == employee_id,
        )
    ).first()
    if employee_link is None:
        raise HTTPException(status_code=404, detail=detail)
    return employee_link


def get_employee_business_link_or_404(
    db: Session,
    employee_id: UUID | str,
    detail: str = "Employee not found",
) -> Business_Employee:
    employee_link = db.exec(
        select(Business_Employee).where(Business_Employee.employee_id == employee_id)
    ).first()
    if employee_link is None:
        raise HTTPException(status_code=404, detail=detail)
    return employee_link


def get_listing_for_business_or_404(
    db: Session,
    business_id: UUID | str,
    listing_id: UUID | str,
    detail: str = "Listing not found",
    ownership_detail: str = "Listing does not belong to this business",
) -> Listing:
    listing = get_listing_or_404(db, listing_id, detail=detail)
    if str(listing.business_id) != str(business_id):
        raise HTTPException(status_code=403, detail=ownership_detail)
    return listing


def get_owned_itinerary_or_404(
    db: Session,
    itinerary_id: UUID | str,
    user_id: UUID | str,
    *,
    load_items: bool = False,
    detail: str = "Itinerary not found",
) -> Itinerary:
    query = select(Itinerary).where(
        Itinerary.id == itinerary_id,
        Itinerary.user_id == user_id,
    )
    if load_items:
        query = query.options(selectinload(Itinerary.items))

    itinerary = db.exec(query).first()
    if itinerary is None:
        raise HTTPException(status_code=404, detail=detail)
    return itinerary


def get_owned_itinerary_item_context_or_404(
    db: Session,
    itinerary_item_id: UUID | str,
    user_id: UUID | str,
) -> tuple:
    itinerary_item = get_itinerary_item_or_404(db, itinerary_item_id)
    itinerary = get_owned_itinerary_or_404(db, itinerary_item.itinerary_id, user_id)
    ensure_itinerary_owner(itinerary, user_id)
    return itinerary_item, itinerary
