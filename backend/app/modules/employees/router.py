from fastapi import APIRouter, Depends, HTTPException, status
from app.infrastructure.database import get_db
from app.modules.businesses.service import (
    add_business_employee,
    add_employee_to_listing,
    get_business_employees,
    remove_employee_from_listing as remove_employee_from_listing_service,
)
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_roles
from sqlmodel import Session
from uuid import UUID

from .schemas import EmployeeCreate, EmployeeResponse
from .service import get_employee_listings


router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get("")
def list_employees(
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    return get_business_employees(db, current_user.id)


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(
    employee_data: EmployeeCreate,
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    return add_business_employee(
        db=db,
        business_owner_id=current_user.id,
        email=employee_data.email,
        password=employee_data.password,
        username=employee_data.username,
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        phone=employee_data.phone,
    )


@router.post("/{employee_id}/listings/{listing_id}", response_model=dict, status_code=201)
def assign_employee_to_listing(
    employee_id: UUID,
    listing_id: UUID,
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    return add_employee_to_listing(
        db=db,
        business_owner_id=current_user.id,
        employee_id=employee_id,
        listing_id=listing_id,
    )

@router.delete("/{employee_id}/listings/{listing_id}", response_model=dict, status_code=201)
def remove_employee_from_listing(
    employee_id: UUID,
    listing_id: UUID,
    current_user: User = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db),
):
    return remove_employee_from_listing_service(
        db=db,
        business_owner_id=current_user.id,
        employee_id=employee_id,
        listing_id=listing_id,
    )

@router.get("/{employee_id}/listings")
def list_employee_listings(
    employee_id: UUID,
    current_user: User = Depends(require_roles("business", "admin", "employee")),
    db: Session = Depends(get_db),
):
    if current_user.user_type == "employee" and current_user.id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this resource",
        )
    return get_employee_listings(db, employee_id)
