from uuid import UUID

from sqlmodel import Session, select
from app.modules.users.models import User
from .models import Business_Employee
from app.modules.businesses.models import Business


def get_business_employees(db: Session, user_id: UUID) -> list[dict]:
    business = db.exec(select(Business).where(Business.user_id == user_id)).first()
    if not business:
        return []
    employees = db.exec(
        select(Business_Employee, User)
        .join(User, Business_Employee.user_id == User.id)
        .where(Business_Employee.business_id == business.id)
    ).all()
    return [
        {
            "id": str(employee.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
        }
        for employee, user in employees
    ]
