from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.modules.businesses.models import Business
from app.modules.listings.models import EmployeeListings, Listing
from app.modules.listings.service import serialize_listings
from app.modules.users.models import User
from app.shared.domain import (
    get_employee_business_link_or_404,
    get_listing_for_business_or_404,
    get_owned_business_or_404,
)

from .models import Business_Employee


def get_employee_listings(db: Session, employee_id: UUID):
    get_employee_business_link_or_404(db, employee_id)

    listings = db.exec(
        select(Listing)
        .join(EmployeeListings, EmployeeListings.listing_id == Listing.id)
        .where(EmployeeListings.employee_id == employee_id)
        .options(selectinload(Listing.business_type_rel))
    ).all()

    return serialize_listings(db, listings)


def get_employees_for_listing(db: Session, listing_id: UUID, business_owner_id: UUID):
    business = get_owned_business_or_404(db, business_owner_id)
    get_listing_for_business_or_404(
        db,
        business.id,
        listing_id,
        detail="Listing not found or access denied",
        ownership_detail="Listing not found or access denied",
    )

    employees = db.exec(
        select(Business_Employee, User)
        .join(User, Business_Employee.employee_id == User.id)
        .join(EmployeeListings, EmployeeListings.employee_id == Business_Employee.employee_id)
        .where(
            EmployeeListings.listing_id == listing_id,
            Business_Employee.business_id == business.id,
        )
    ).all()

    return [
        {
            "id": str(employee.id),
            "employee_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "business_id": str(employee.business_id),
        }
        for employee, user in employees
    ]
