"""Router for availability module."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.infrastructure.database.session import get_db

from .schemas import (
    ListingHoursCreate,
    ListingHoursResponse,
    ListingHoursUpdate,
    ServiceSlotsCreate,
    ServiceSlotsResponse,
    ServiceSlotsUpdate,
)
from . import service as availability_service

router = APIRouter(prefix="/api/availability", tags=["availability"])


# ============================================================================
# ListingHours Endpoints
# ============================================================================


@router.post("/listings/{listing_id}/hours", response_model=ListingHoursResponse, status_code=201)
def create_listing_hours(
    listing_id: UUID,
    data: ListingHoursCreate,
    db: Session = Depends(get_db),
):
    """Create hours for a specific day of the week."""
    if data.listing_id != listing_id:
        raise HTTPException(400, "listing_id in path must match body")
    return availability_service.create_listing_hours(db, data)


@router.get("/listings/{listing_id}/hours", response_model=list[ListingHoursResponse])
def list_listing_hours(
    listing_id: UUID,
    db: Session = Depends(get_db),
):
    """List all hours for a listing."""
    return availability_service.list_listing_hours(db, listing_id)


@router.put("/listings/{listing_id}/hours/{day}", response_model=ListingHoursResponse)
def update_listing_hours(
    listing_id: UUID,
    day: int,
    data: ListingHoursUpdate,
    db: Session = Depends(get_db),
):
    """Update hours for a specific day."""
    return availability_service.update_listing_hours(db, listing_id, day, data)


@router.delete("/listings/{listing_id}/hours/{day}", status_code=204)
def delete_listing_hours(
    listing_id: UUID,
    day: int,
    db: Session = Depends(get_db),
):
    """Delete hours for a specific day."""
    availability_service.delete_listing_hours(db, listing_id, day)


# ============================================================================
# ServiceSlots Endpoints
# ============================================================================


@router.post("/services/{service_id}/slots", response_model=ServiceSlotsResponse, status_code=201)
def create_service_slot(
    service_id: UUID,
    data: ServiceSlotsCreate,
    db: Session = Depends(get_db),
):
    """Create a new service slot."""
    if data.service_id != service_id:
        raise HTTPException(400, "service_id in path must match body")
    return availability_service.create_service_slot(db, data)


@router.get("/services/{service_id}/slots", response_model=list[ServiceSlotsResponse])
def list_service_slots(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    """List all slots for a service."""
    return availability_service.list_service_slots(db, service_id)


@router.delete("/services/{service_id}/slots/{slot_id}", status_code=204)
def delete_service_slot(
    service_id: UUID,
    slot_id: int,
    db: Session = Depends(get_db),
):
    """Delete a service slot."""
    availability_service.delete_service_slot(db, slot_id)