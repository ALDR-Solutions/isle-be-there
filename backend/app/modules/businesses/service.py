from fastapi import HTTPException
from sqlmodel import Session, select
from uuid import UUID

from app.modules.businesses.models import Business, BusinessType
from app.modules.listings.models import EmployeeListings, Listing
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.modules.users.service import create_user

from app.modules.employees.models import Business_Employee


def list_businesses(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    verified_only: bool = False,
):
    query = select(Business)
    if verified_only:
        query = query.where(Business.is_verified == True)

    businesses = db.exec(query.order_by(Business.business_name).offset(skip).limit(limit)).all()
    return [business.model_dump() for business in businesses]


def get_business_by_id(db: Session, business_id: UUID) -> Business | None:
    business = db.exec(select(Business).where(Business.id == business_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business.model_dump()


def get_business_by_user_id(db: Session, user_id: UUID) -> Business | None:
    return db.exec(select(Business).where(Business.user_id == user_id)).first()


def list_business_types(db: Session):
    return db.exec(select(BusinessType)).all()


def create_business(db: Session, data: dict, user_id: UUID):
    existing = get_business_by_user_id(db, user_id)
    if existing:
        raise HTTPException(status_code=400, detail="User already has a business")

    data["user_id"] = user_id
    business = Business(**data)
    db.add(business)
    db.commit()
    db.refresh(business)
    return business.model_dump()


def update_business(
    db: Session,
    business_id: str,
    update_data: dict,
    user_id: str,
    is_admin: bool = False,
):
    business = db.exec(select(Business).where(Business.id == business_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if not is_admin and str(business.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in update_data.items():
        setattr(business, key, value)
    db.commit()
    db.refresh(business)
    return business.model_dump()

def get_business_employees(db: Session, user_id: UUID) -> list[dict]:
    business = db.exec(select(Business).where(Business.user_id == user_id)).first()
    if not business:
        return []
    employees = db.exec(
        select(Business_Employee, User)
        .join(User, Business_Employee.employee_id == User.id)
        .where(Business_Employee.business_id == business.id)
    ).all()
    return [
        {
            "id": str(employee.id),
            "employee_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
        }
        for employee, user in employees
    ]


def add_business_employee(
    db: Session,
    business_owner_id: UUID,
    email: str,
    password: str,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
) -> dict:
    business = db.exec(select(Business).where(Business.user_id == business_owner_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found for this user")

    existing_user = db.exec(select(User).where(User.email == email)).first()
    if existing_user:
        existing_link = db.exec(
            select(Business_Employee).where(
                Business_Employee.business_id == business.id,
                Business_Employee.employee_id == existing_user.id,
            )
        ).first()
        if existing_link:
            raise HTTPException(
                status_code=400,
                detail="Employee with this email is already assigned to this business",
            )
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Use a different email to create a new employee user",
        )

    new_user = create_user(
        db,
        UserCreate(
            email=email,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            user_type="employee",
        ),
    )

    if phone:
        new_user.phone = phone
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    business_employee = Business_Employee(
        business_id=business.id,
        employee_id=new_user.id,
    )
    db.add(business_employee)
    db.commit()
    db.refresh(business_employee)

    return {
        "id": str(business_employee.id),
        "business_id": str(business.id),
        "employee_id": str(new_user.id),
        "email": new_user.email,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "phone": new_user.phone,
    }

def update_business_employee(
    db: Session,
    business_owner_id: UUID,
    employee_id: UUID,
    email: str | None = None,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
) -> dict:
    business = db.exec(select(Business).where(Business.user_id == business_owner_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found for this user")

    employee_link = db.exec(
        select(Business_Employee).where(
            Business_Employee.business_id == business.id,
            Business_Employee.employee_id == employee_id,
        )
    ).first()
    
    if not employee_link:
        raise HTTPException(status_code=404, detail="Employee not found for this business")

    user = db.exec(select(User).where(User.id == employee_link.employee_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User associated with this employee not found")

    if email and email != user.email:
        existing_user = db.exec(select(User).where(User.email == email)).first()
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=400, detail="Email already registered to another user")
        user.email = email

    if username is not None:
        user.username = username

    if first_name is not None:
        user.first_name = first_name

    if last_name is not None:
        user.last_name = last_name

    if phone is not None:
        user.phone = phone

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": str(employee_link.id),
        "business_id": str(business.id),
        "employee_id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
    }

def add_employee_to_listing(
    db: Session,
    business_owner_id: UUID,
    employee_id: UUID,
    listing_id: UUID,
) -> dict:
    business = db.exec(select(Business).where(Business.user_id == business_owner_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found for this user")

    employee_link = db.exec(
        select(Business_Employee).where(
            Business_Employee.business_id == business.id,
            Business_Employee.employee_id == employee_id,
        )
    ).first()
    if not employee_link:
        raise HTTPException(status_code=404, detail="Employee not found for this business")

    listing = db.exec(select(Listing).where(Listing.id == listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if str(listing.business_id) != str(business.id):
        raise HTTPException(status_code=403, detail="Listing does not belong to this business")

    existing_assignment = db.exec(
        select(EmployeeListings).where(
            EmployeeListings.employee_id == employee_id,
            EmployeeListings.listing_id == listing_id,
        )
    ).first()
    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail="Employee is already assigned to this listing",
        )

    assignment = EmployeeListings(
        employee_id=employee_id,
        listing_id=listing_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "id": str(assignment.id),
        "employee_id": str(assignment.employee_id),
        "listing_id": str(assignment.listing_id),
    }
    
def remove_employee_from_listing(
    db: Session,
    business_owner_id: UUID,
    employee_id: UUID,
    listing_id: UUID,
) -> dict:
    business = db.exec(select(Business).where(Business.user_id == business_owner_id)).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found for this user")
    employee_link = db.exec(
        select(Business_Employee).where(
            Business_Employee.business_id == business.id,
            Business_Employee.employee_id == employee_id,
        )
    ).first()
    if not employee_link:
        raise HTTPException(status_code=404, detail="Employee not found for this business")

    listing = db.exec(select(Listing).where(Listing.id == listing_id)).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if str(listing.business_id) != str(business.id):
        raise HTTPException(status_code=403, detail="Listing does not belong to this business")

    assignment = db.exec(
        select(EmployeeListings).where(
            EmployeeListings.employee_id == employee_id,
            EmployeeListings.listing_id == listing_id,
        )
    ).first()
    if not assignment:
        raise HTTPException(
            status_code=400,
            detail="Employee is not assigned to this listing",
        )

    db.delete(assignment)
    db.commit()

    return {
        "id": str(assignment.id),
        "employee_id": str(assignment.employee_id),
        "listing_id": str(assignment.listing_id),
    }
    
