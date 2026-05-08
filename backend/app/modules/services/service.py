from uuid import UUID
from sqlalchemy import asc, func, select
from sqlmodel import Session

from fastapi import HTTPException

from app.modules.services.models import Service, StatusTypes
from app.modules.services.schemas import ServiceCreate, ServiceUpdate
from app.modules.listings.models import Listing




def _get_service(db: Session, service_id: UUID) -> Service | None:
    return db.exec(
        select(Service).where(Service.service_id == service_id)
    ).scalars().first()


def _get_listing(db: Session, listing_id: UUID) -> Listing | None:
    return db.exec(
        select(Listing).where(Listing.id == listing_id)
    ).scalars().first()


def get_service_by_id(db: Session, service_id: UUID) -> Service:
    service = _get_service(db, service_id)
    if not service:
        raise HTTPException(404, "Service not found")
    return service


def get_services(db: Session) -> list[Service]:
    return db.exec(
        select(Service)
        .where(Service.status == StatusTypes.active)
        .order_by(asc(Service.created_at))
    ).scalars().all()


def get_services_by_listing(db: Session, listing_id: UUID, user_type: str) -> list[Service]:
    query = select(Service).where(Service.listing_id == listing_id)

    if user_type == "regular":
        query = query.where(Service.status == StatusTypes.active)
    elif user_type == "business" or user_type == "employee":
        query = query.where(Service.status != StatusTypes.deleted)
   

    return db.exec(query.order_by(asc(Service.created_at))).scalars().all()


def create_service(db: Session, data: ServiceCreate, user_id: UUID) -> Service:
    if not data.listing_id:
        raise HTTPException(400, "listing_id is required")

    listing = _get_listing(db, data.listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")

    service = Service(**data.model_dump(), user_id=user_id)

    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def update_service(db: Session, service_id: UUID, data: ServiceUpdate) -> Service:
    service = _get_service(db, service_id)
    if not service:
        raise HTTPException(404, "Service not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(service, k, v)

    service.updated_at = func.now()
    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, service_id: UUID) -> Service:
    service = _get_service(db, service_id)
    if not service:
        raise HTTPException(404, "Service not found")

    service.status = StatusTypes.deleted
    service.updated_at = func.now()

    db.commit()
    db.refresh(service)
    return service


def deactivate_service(db: Session, service_id: UUID) -> Service:
    service = _get_service(db, service_id)
    if not service:
        raise HTTPException(404, "Service not found")

    service.status = StatusTypes.inactive
    service.updated_at = func.now()

    db.commit()
    db.refresh(service)
    return service