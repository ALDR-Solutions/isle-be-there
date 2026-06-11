from types import SimpleNamespace
from uuid import uuid4

from app.modules.bookings import service as bookings_service
from app.modules.discounts import service as discounts_service
from app.modules.pricing import service as pricing_service


def test_calculate_discount_for_amount_uses_fractional_percent():
    assert discounts_service.calculate_discount_for_amount(250, 0.10, None) == 25.0
    assert discounts_service.calculate_discount_for_amount(250, 10, None) == 25.0


def test_calculate_display_price_normalizes_legacy_service_fee_percent(monkeypatch):
    listing_id = uuid4()
    service_id = uuid4()

    class FakeDb:
        def get(self, model, record_id):
            if record_id == listing_id:
                return SimpleNamespace(id=listing_id, base_price=200, business_type_id=None)
            raise AssertionError(f"Unexpected lookup: {record_id}")

    monkeypatch.setattr(
        pricing_service,
        "get_service_by_id",
        lambda db, sid: SimpleNamespace(service_id=sid, price=120) if sid == service_id else None,
    )
    monkeypatch.setattr(
        pricing_service,
        "get_pricing_config",
        lambda db, business_type_id=None: SimpleNamespace(service_fee_percent=10),
    )

    result = pricing_service.calculate_display_price(FakeDb(), listing_id, service_id)

    assert result["base_price"] == 120
    assert result["service_fee_percent"] == 0.10
    assert result["service_fee_amount"] == 12.0
    assert result["display_price"] == 132.0


def test_price_booking_from_itinerary_item_applies_eligible_package_discount(monkeypatch):
    itinerary_item_id = uuid4()
    listing_id = uuid4()
    service = SimpleNamespace(listing_id=listing_id, service_id=uuid4())
    itinerary = SimpleNamespace(id=uuid4())

    monkeypatch.setattr(
        bookings_service,
        "get_owned_itinerary_item_context_or_404",
        lambda db, item_id, user_id: (
            SimpleNamespace(id=item_id, listing_id=listing_id),
            itinerary,
        ),
    )
    monkeypatch.setattr(
        bookings_service,
        "calculate_display_price",
        lambda db, next_listing_id, next_service_id=None: {
            "base_price": 100.0,
            "service_fee_percent": 0.10,
        },
    )
    monkeypatch.setattr(bookings_service, "is_hotel_service", lambda db, next_service: False)
    monkeypatch.setattr(
        bookings_service,
        "get_eligible_package_discount",
        lambda db, next_itinerary: SimpleNamespace(discount_percent=0.20, max_discount_amount=None),
    )

    result = bookings_service.price_booking_from_itinerary_item(
        db=object(),
        itinerary_item_id=itinerary_item_id,
        user_id=uuid4(),
        service=service,
        amount_of_people=2,
    )

    assert result["base_price"] == 200.0
    assert result["service_fee_percent"] == 0.10
    assert result["service_fee_amount"] == 20.0
    assert result["display_price"] == 220.0
    assert result["discount_percent"] == 0.20
    assert result["discount_amount"] == 44.0
    assert result["final_price"] == 176.0
