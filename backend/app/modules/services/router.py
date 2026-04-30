from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from uuid import UUID

from app.infrastructure.database import get_db
from app.modules.users.models import User
from app.shared.dependencies.permissions import (
    require_roles,
    require_service_access
)

from .models import Service
from .schemas import ServiceCreate, ServiceResponse, ServiceUpdate
from .service import (
    create_service,
    update_service,
    delete_service,
    deactivate_service,
    get_services,
    get_services_by_listing,
)

router = APIRouter(prefix="/api/services", tags=["Services"])



@router.get("", response_model=List[ServiceResponse])
def get_services_endpoint(
    listing_id: UUID | None = None,
    user: User = Depends(require_roles("regular", "business", "admin", "employee")),
    db: Session = Depends(get_db),
):

    return get_services_by_listing(db, listing_id, user.user_type)




@router.get("/{service_id}", response_model=ServiceResponse)
def get_service_endpoint(
    service: Service = Depends(require_service_access)
):
    return service



@router.post("", response_model=ServiceResponse, status_code=201)
def create_service_endpoint(
    data: ServiceCreate,
    user: User = Depends(require_roles("business", "employee")),
    db: Session = Depends(get_db)
):
    return create_service(db, data, user.id)



@router.put("/{service_id}", response_model=ServiceResponse)
def update_service_endpoint(
    data: ServiceUpdate,
    service: Service = Depends(require_service_access),
    db: Session = Depends(get_db)
):
    return update_service(
        db,
        service.service_id,
        data.model_dump(exclude_unset=True),
    )


@router.delete("/{service_id}", response_model=ServiceResponse)
def delete_service_endpoint(
    service: Service = Depends(require_service_access),
    db: Session = Depends(get_db),
):
    return delete_service(db, service.service_id)


@router.patch("/{service_id}/archive", response_model=ServiceResponse)
def archive_service_endpoint(
    service: Service = Depends(require_service_access),
    db: Session = Depends(get_db),
):
    return deactivate_service(db, service.service_id)