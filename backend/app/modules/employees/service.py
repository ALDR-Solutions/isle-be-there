from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.modules.listings.models import EmployeeListings, Listing

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
