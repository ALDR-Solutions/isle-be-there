"""Business logic for services."""

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, asc, select

from app.modules.listings.models import EmployeeListings, Listing

from .models import Service


def get_service_by_id(db: Session, service_id: str):
    service = db.exec(
        select(Service)
        .where(Service.service_id == service_id)
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


def get_services(db: Session) -> list:
    services = db.exec(
        select(Service)
        .where(Service.status == "active")
        .order_by(asc(Service.created_at))
    ).all()
    return services


def get_services_by_listing_id(db: Session, listing_id: str, user_type: str) -> list:
    if user_type in ["business", "employee"]:
        services = db.exec(
            select(Service)
            .where((Service.listing_id == listing_id) & (Service.status != "deleted"))
            .order_by(asc(Service.created_at))
        ).all()
    elif user_type in ["admin"]:
        services = db.exec(
            select(Service)
            .where(Service.listing_id == listing_id)
            .order_by(asc(Service.created_at))
        ).all()
    else:
        services = db.exec(
            select(Service).where(
                (Service.listing_id == listing_id) & (Service.status == "active")
            ).order_by(asc(Service.created_at))
        ).all()
    return services


def _get_listing_or_404(db: Session, listing_id: str) -> Listing:
    listing = db.exec(
        select(Listing)
        .where(Listing.id == listing_id)
        .options(selectinload(Listing.business_rel))
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


def _ensure_listing_service_access(db: Session, listing: Listing, user_id: str, detail: str):
    business = listing.business_rel
    if business and business.user_id == user_id:
        return

    assignment = db.exec(
        select(EmployeeListings).where(
            EmployeeListings.listing_id == listing.id,
            EmployeeListings.employee_id == user_id,
        )
    ).first()
    if assignment:
        return

    raise HTTPException(status_code=403, detail=detail)


def create_service(db: Session, service: Service, user_id: str) -> Service:
    listing = _get_listing_or_404(db, service.listing_id)
    _ensure_listing_service_access(
        db,
        listing,
        user_id,
        "Not authorized to add service to this listing",
    )

    db.add(service)
    db.commit()
    db.refresh(service)
    return service


def update_service(db: Session, service_id: str, update_data: dict, user_id: str) -> Service:
    service = db.exec(
        select(Service)
        .where(Service.service_id == service_id)
    ).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    listing = _get_listing_or_404(db, service.listing_id)
    _ensure_listing_service_access(
        db,
        listing,
        user_id,
        "Not authorized to update this service",
    )

    for key, value in update_data.items():
        setattr(service, key, value)

    service.updated_at = func.now()
    db.commit()
    db.refresh(service)
    return service


def delete_service(db: Session, service_id: str, user_id: str):
    service = db.exec(select(Service).where(Service.service_id == service_id)).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    listing = _get_listing_or_404(db, service.listing_id)
    _ensure_listing_service_access(
        db,
        listing,
        user_id,
        "Not authorized to delete this service",
    )

    service.status = "deleted"
    service.updated_at = func.now()
    db.commit()
    db.refresh(service)
    return service


def deactivate_service(db: Session, service_id: str, user_id: str):
    service = db.exec(select(Service).where(Service.service_id == service_id)).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    listing = _get_listing_or_404(db, service.listing_id)
    _ensure_listing_service_access(
        db,
        listing,
        user_id,
        "Not authorized to deactivate this service",
    )

    service.status = "inactive"
    service.updated_at = func.now()
    db.commit()
    db.refresh(service)
    return service
