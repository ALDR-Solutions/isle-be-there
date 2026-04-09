from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.businesses.models import Business
from app.modules.listings.models import EmployeeListings, Listing
from app.modules.users.models import User

from .models import Business_Employee

def get_employee_listings(db: Session, employee_id: UUID):
    employee_link = db.exec(
        select(Business_Employee).where(Business_Employee.employee_id == employee_id)
    ).first()
    if not employee_link:
        raise HTTPException(status_code=404, detail="Employee not found")

    listings = db.exec(
        select(Listing)
        .join(EmployeeListings, EmployeeListings.listing_id == Listing.id)
        .where(EmployeeListings.employee_id == employee_id)
    ).all()

    return [
        listing.model_dump(exclude={"embedding", "location"})
        for listing in listings
    ]


def get_employees_for_listing(db: Session, listing_id: UUID, business_owner_id: UUID):
    # Verify listing exists and belongs to a business owned by the requester
    result = db.exec(
        select(Listing, Business)
        .join(Business, Business.id == Listing.business_id)
        .where(
            Listing.id == listing_id,
            Business.user_id == business_owner_id,
        )
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Listing not found or access denied")

    _, business = result

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
