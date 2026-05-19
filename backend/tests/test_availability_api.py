"""Integration tests for availability API endpoints."""

from datetime import time
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.infrastructure.database.session import get_db
from app.modules.availability.models import ListingHours, ServiceSlots
from app.modules.listings.models import Listing
from app.modules.services.models import Service
from sqlmodel import Session, col, delete, select


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def db():
    """Get database session."""
    with next(get_db().__iter__()) as session:
        yield session
        session.rollback()


@pytest.fixture
def listing(db: Session):
    """Create a test listing."""
    listing = Listing(
        title="Test Listing",
        description="Test description",
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    yield listing
    # Cleanup
    db.exec(delete(ListingHours).where(ListingHours.listing_id == listing.id))
    db.delete(listing)
    db.commit()


class TestListingHoursAPI:
    """Test ListingHours CRUD endpoints."""

    def test_create_listing_hours(self, client: TestClient, db: Session, listing):
        """POST /api/availability/listings/{id}/hours creates hours."""
        response = client.post(
            f"/api/availability/listings/{listing.id}/hours",
            json={
                "listing_id": str(listing.id),
                "day_of_week": 1,
                "open_time": "09:00:00",
                "close_time": "18:00:00",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["listing_id"] == str(listing.id)
        assert data["day_of_week"] == 1
        assert data["open_time"] == "09:00:00"
        assert data["close_time"] == "18:00:00"

    def test_list_listing_hours(self, client: TestClient, db: Session, listing):
        """GET /api/availability/listings/{id}/hours returns list."""
        # Create some hours
        hours = ListingHours(
            listing_id=listing.id,
            day_of_week=1,
            open_time=time(9, 0),
            close_time=time(18, 0),
        )
        db.add(hours)
        db.commit()

        response = client.get(f"/api/availability/listings/{listing.id}/hours")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["day_of_week"] == 1

    def test_update_listing_hours(self, client: TestClient, db: Session, listing):
        """PUT /api/availability/listings/{id}/hours/{day} updates hours."""
        # Create hours first
        hours = ListingHours(
            listing_id=listing.id,
            day_of_week=1,
            open_time=time(9, 0),
            close_time=time(18, 0),
        )
        db.add(hours)
        db.commit()

        response = client.put(
            f"/api/availability/listings/{listing.id}/hours/1",
            json={
                "open_time": "10:00:00",
                "close_time": "20:00:00",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["open_time"] == "10:00:00"
        assert data["close_time"] == "20:00:00"

    def test_delete_listing_hours(self, client: TestClient, db: Session, listing):
        """DELETE /api/availability/listings/{id}/hours/{day} removes hours."""
        # Create hours first
        hours = ListingHours(
            listing_id=listing.id,
            day_of_week=1,
            open_time=time(9, 0),
            close_time=time(18, 0),
        )
        db.add(hours)
        db.commit()

        response = client.delete(f"/api/availability/listings/{listing.id}/hours/1")
        assert response.status_code == 204

        # Verify deleted
        remaining = db.exec(
            select(ListingHours).where(ListingHours.listing_id == listing.id)
        ).all()
        assert len(remaining) == 0

    def test_duplicate_day_conflict(self, client: TestClient, db: Session, listing):
        """Creating duplicate day returns 409."""
        # Create first hours
        hours = ListingHours(
            listing_id=listing.id,
            day_of_week=1,
            open_time=time(9, 0),
            close_time=time(18, 0),
        )
        db.add(hours)
        db.commit()

        # Try to create again
        response = client.post(
            f"/api/availability/listings/{listing.id}/hours",
            json={
                "listing_id": str(listing.id),
                "day_of_week": 1,
                "open_time": "10:00:00",
                "close_time": "20:00:00",
            },
        )
        assert response.status_code == 409


class TestServiceSlotsAPI:
    """Test ServiceSlots CRUD endpoints."""

    @pytest.fixture
    def service(self, db: Session, listing):
        """Create a test service associated with the test listing."""
        # Add listing hours (required for service slot creation validation)
        listing_hours = ListingHours(
            listing_id=listing.id,
            day_of_week=1,  # Monday
            open_time=time(9, 0),
            close_time=time(18, 0),
        )
        db.add(listing_hours)
        db.commit()

        service = Service(
            name="Test Service",
            description="Test description",
            capacity=10,
            listing_id=listing.id,
        )
        db.add(service)
        db.commit()
        db.refresh(service)
        yield service
        # Cleanup
        db.exec(delete(ServiceSlots).where(ServiceSlots.service_id == service.service_id))
        db.delete(service)
        db.commit()

    def test_create_service_slot(self, client: TestClient, db: Session, service):
        """POST /api/availability/services/{id}/slots creates slot."""
        response = client.post(
            f"/api/availability/services/{service.service_id}/slots",
            json={
                "service_id": str(service.service_id),
                "day_of_week": 1,
                "start_time": "09:00:00",
                "end_time": "11:00:00",
                "capacity": 5,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["service_id"] == str(service.service_id)
        assert data["day_of_week"] == 1
        assert data["start_time"] == "09:00:00"
        assert data["end_time"] == "11:00:00"
        assert data["capacity"] == 5

    def test_list_service_slots(self, client: TestClient, db: Session, service):
        """GET /api/availability/services/{id}/slots returns list."""
        # Create a slot
        slot = ServiceSlots(
            service_id=service.service_id,
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=5,
        )
        db.add(slot)
        db.commit()

        response = client.get(f"/api/availability/services/{service.service_id}/slots")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["day_of_week"] == 1

    def test_delete_service_slot(self, client: TestClient, db: Session, service):
        """DELETE /api/availability/services/{id}/slots/{slot_id} removes slot."""
        # Create a slot
        slot = ServiceSlots(
            service_id=service.service_id,
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=5,
        )
        db.add(slot)
        db.commit()
        slot_id = slot.id

        response = client.delete(f"/api/availability/services/{service.service_id}/slots/{slot_id}")
        assert response.status_code == 204

        # Verify deleted
        remaining = db.exec(
            select(ServiceSlots).where(ServiceSlots.service_id == service.service_id)
        ).all()
        assert len(remaining) == 0

    def test_slot_start_after_end_invalid(self, client: TestClient, service):
        """Slot with start_time >= end_time returns 422."""
        response = client.post(
            f"/api/availability/services/{service.service_id}/slots",
            json={
                "service_id": str(service.service_id),
                "day_of_week": 1,
                "start_time": "14:00:00",
                "end_time": "11:00:00",
                "capacity": 5,
            },
        )
        assert response.status_code == 422