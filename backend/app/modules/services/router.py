from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.infrastructure.database import get_db
from app.modules.auth import service
from app.modules.users.models import User
from app.shared.dependencies.permissions import require_listing_owner, require_roles

from .models import Service
from .schemas import ServiceCreate, ServiceResponse, ServiceUpdate
from .service import (
    create_service,
    deactivate_service,
    delete_service,
    get_service_by_id,
    get_services,
    get_services_by_listing_id,
    update_service,
)

router = APIRouter(prefix="/api/services", tags=["Services"])

def _require_user_id(user_id: str | None):
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    

@router.get("", response_model=List[ServiceResponse])
def get_services_by_listing_id_endpoint(
    listing_id: str | None = None,
    current_user: User = Depends(require_roles("user", "business", "admin", "employee")),
    db: Session = Depends(get_db),
):
    
    return get_services_by_listing_id(db=db, listing_id=listing_id, user_type=current_user.user_type)

@router.get("/", response_model=List[ServiceResponse])
def get_service_endpoint(
    db: Session = Depends(get_db),
):
    
    return get_services(db=db)

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service_by_id_endpoint(
    service_id: str,
    db: Session = Depends(get_db),
):
    
    return get_service_by_id(db=db, service_id=service_id)


@router.post("/create", response_model=ServiceResponse, status_code=201)
def create_service_endpoint(
    service_data: ServiceCreate,
    current_user: User = Depends(require_roles("business","employee")),
    db: Session = Depends(get_db),
):
    
    _require_user_id(current_user.id)
    service = Service(**service_data.model_dump(exclude_unset=True))
    return create_service(db, service, current_user.id)


@router.put("/update/{service_id}", response_model=ServiceResponse)
def update_service_endpoint(
    service_data: ServiceUpdate,
    service_id: str,
    current_user: User = Depends(require_roles("business","employee")),
    db: Session = Depends(get_db),
):
    
    update_data = {
        key: value
        for key, value in service_data.model_dump(exclude_unset=True).items()
        if value is not None
    }

    return update_service(db, service_id, update_data, current_user.id)


@router.delete("/{service_id}", response_model=ServiceResponse)
def delete_service_endpoint(
    service_id: str,
    current_user: User = Depends(require_roles("business","employee")),
    db: Session = Depends(get_db),
):
    
    return delete_service(db, service_id, current_user.id)

@router.patch("/{service_id}", response_model=ServiceResponse)
def archive_service_endpoint(
    service_id: str,
    current_user: User = Depends(require_roles("business","employee")),
    db: Session = Depends(get_db),
):
    
    return deactivate_service(db, service_id, current_user.id)