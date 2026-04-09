"""Business logic for services."""
import random

from fastapi import HTTPException
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy import func
from sqlalchemy.sql.functions import count
from sqlalchemy.orm import selectinload
from sqlmodel import Session, asc, desc, select

from app.modules.businesses import service
from app.modules.businesses.models import Business
from app.modules.listings.models import Listing
from app.modules.users.models import User

from .models import Service




def get_service_by_id(db: Session, service_id: str):
    service = db.exec(
        select(Service)
        .where(Service.service_id == service_id)
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")


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
            select(Service)
            .where((Service.listing_id == listing_id)&(Service.status == "active"))
            .order_by(asc(Service.created_at))
        ).all()
    return services

def create_service(db: Session, service: Service, user_id: str) -> Service:
    # Verify listing exists and user has permission to add service
    listing = db.exec(
        select(Listing)
        .where(Listing.id == service.listing_id)
        .options(selectinload(Listing.business_rel))
    ).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    business = listing.business_rel
    if business.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add service to this listing")

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

    listing = db.exec(
        select(Listing)
        .where(Listing.id == service.listing_id)
        .options(selectinload(Listing.business_rel))
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    business = listing.business_rel
    if business.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this service")

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

    listing = db.exec(
        select(Listing)
        .where(Listing.id == service.listing_id)
        .options(selectinload(Listing.business_rel))
    ).first()


    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    business = listing.business_rel
    if business.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this service")

    service.status = "deleted"
    service.updated_at = func.now()
    db.commit()
    db.refresh(service)
    return service

def deactivate_service(db: Session, service_id: str, user_id: str):
    service = db.exec(select(Service).where(Service.service_id == service_id)).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    listing = db.exec(
        select(Listing)
        .where(Listing.id == service.listing_id)
        .options(selectinload(Listing.business_rel))
    ).first()


    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    business = listing.business_rel
    if business.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this service")

    service.status = "inactive"
    service.updated_at = func.now()
    db.commit()
    db.refresh(service)
    return service