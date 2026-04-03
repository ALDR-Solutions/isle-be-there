from fastapi import APIRouter, Depends
from app.shared.dependencies.permissions import require_roles
from sqlmodel import Session
from app.infrastructure.database import get_db
from .service import get_business_employees


router = APIRouter(prefix="/api/employees", tags=["Employees"])

@router.get("")
def list_employees(
    current_user = Depends(require_roles("business", "admin")),
    db: Session = Depends(get_db)
):
    return get_business_employees(db, current_user.id)