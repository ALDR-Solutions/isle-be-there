from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
import sys

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.service import create_booking
from app.modules.businesses.models import Business, BusinessType  # noqa: F401
from app.modules.itineraries.models import Itinerary, ItineraryItem
from app.modules.services.models import Service
from app.modules.services.models import StatusTypes


class FakeSession:
    def __init__(self, objects=None):
        self.objects = objects or {}
        self.added = None
        self.committed = False
        self.rolled_back = False

    def get(self, model, object_id):
        return self.objects.get((model, object_id))

    def add(self, instance):
        self.added = instance

    def commit(self):
        self.committed = True

    def refresh(self, instance):
        return instance

    def rollback(self):
        self.rolled_back = True


def make_booking_data(**overrides):
    payload = {
        "service_id": uuid4(),
        "bookers_name": "Jane Traveler",
        "amount_of_people": 2,
        "booking_from_time": datetime.utcnow(),
        "booking_to_time": datetime.utcnow() + timedelta(hours=2),
        "special_requests": None,
    }
    payload.update(overrides)
    return BookingCreate(**payload)


def make_service(**overrides):
    payload = {
        "service_id": uuid4(),
        "listing_id": uuid4(),
        "status": StatusTypes.active,
        "capacity": 5,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def test_create_booking_succeeds_with_valid_active_service(monkeypatch):
    service = make_service()
    db = FakeSession()
    booking_data = make_booking_data(service_id=service.service_id)

    monkeypatch.setattr(
        "app.modules.bookings.service._validate_service_for_booking",
        lambda *args, **kwargs: (service, None),
    )
    monkeypatch.setattr(
        "app.modules.bookings.service._validate_service_capacity",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "app.modules.bookings.service.calculate_display_price",
        lambda *_args, **_kwargs: {
            "base_price": 150.0,
            "service_fee_percent": 0.1,
            "service_fee_amount": 15.0,
            "display_price": 165.0,
            "final_price": 165.0,
        },
    )

    created = create_booking(db, booking_data, uuid4())

    assert db.committed is True
    assert db.added is created
    assert created.service_id == service.service_id
    assert float(created.base_price) == 150.0
    assert float(created.final_price) == 165.0


def test_create_booking_requires_service_id():
    with pytest.raises(ValidationError):
        BookingCreate(
            bookers_name="Jane Traveler",
            amount_of_people=2,
            booking_from_time=datetime.utcnow(),
            booking_to_time=datetime.utcnow() + timedelta(hours=2),
        )


def test_create_booking_rejects_inactive_service():
    inactive_service = make_service(status=StatusTypes.inactive)
    db = FakeSession({(Service, inactive_service.service_id): inactive_service})
    booking_data = make_booking_data(service_id=inactive_service.service_id)

    with pytest.raises(HTTPException) as exc_info:
        create_booking(db, booking_data, uuid4())

    assert exc_info.value.status_code == 400
    assert "active services" in exc_info.value.detail


def test_create_booking_rejects_service_from_different_itinerary_listing():
    service_id = uuid4()
    itinerary_item_id = uuid4()
    itinerary_id = uuid4()
    user_id = uuid4()
    service = make_service(service_id=service_id, listing_id=uuid4())
    itinerary_item = SimpleNamespace(id=itinerary_item_id, itinerary_id=itinerary_id, listing_id=uuid4())
    itinerary = SimpleNamespace(id=itinerary_id, user_id=user_id)
    db = FakeSession(
        {
            (Service, service_id): service,
            (ItineraryItem, itinerary_item_id): itinerary_item,
            (Itinerary, itinerary_id): itinerary,
        }
    )

    booking_data = make_booking_data(
        service_id=service_id,
        itinerary_item_id=itinerary_item_id,
    )

    with pytest.raises(HTTPException) as exc_info:
        create_booking(db, booking_data, user_id)

    assert exc_info.value.status_code == 400
    assert "does not belong" in exc_info.value.detail


def test_create_booking_rejects_when_capacity_is_exceeded(monkeypatch):
    service = make_service(capacity=2)
    db = FakeSession()
    booking_data = make_booking_data(service_id=service.service_id, amount_of_people=3)

    monkeypatch.setattr(
        "app.modules.bookings.service._validate_service_for_booking",
        lambda *args, **kwargs: (service, None),
    )
    monkeypatch.setattr("app.modules.bookings.service.get_available_slots", lambda *args, **kwargs: 0)

    with pytest.raises(HTTPException) as exc_info:
        create_booking(db, booking_data, uuid4())

    assert exc_info.value.status_code == 409
    assert "not available" in exc_info.value.detail


def test_create_booking_prices_against_the_selected_service(monkeypatch):
    service = make_service()
    db = FakeSession()
    booking_data = make_booking_data(service_id=service.service_id)
    captured = {}

    monkeypatch.setattr(
        "app.modules.bookings.service._validate_service_for_booking",
        lambda *args, **kwargs: (service, None),
    )
    monkeypatch.setattr(
        "app.modules.bookings.service._validate_service_capacity",
        lambda *args, **kwargs: None,
    )

    def fake_calculate_display_price(_db, listing_id, service_id):
        captured["listing_id"] = listing_id
        captured["service_id"] = service_id
        return {
            "base_price": 220.0,
            "service_fee_percent": 0.1,
            "service_fee_amount": 22.0,
            "display_price": 242.0,
            "final_price": 242.0,
        }

    monkeypatch.setattr(
        "app.modules.bookings.service.calculate_display_price",
        fake_calculate_display_price,
    )

    create_booking(db, booking_data, uuid4())

    assert captured == {
        "listing_id": service.listing_id,
        "service_id": service.service_id,
    }
