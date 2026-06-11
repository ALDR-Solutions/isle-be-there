from fastapi.testclient import TestClient

from app.infrastructure.database import get_db
from app.main import create_app
import app.modules.listings.router as listings_router_module


def _override_get_db():
    yield object()


def test_search_listings_requires_lat_and_lng_together():
    app = create_app(background_jobs_enabled=False)
    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as client:
        lat_only_response = client.get("/api/listings/search", params={"lat": 13.1939})
        lng_only_response = client.get("/api/listings/search", params={"lng": -59.5432})

    assert lat_only_response.status_code == 400
    assert lat_only_response.json() == {
        "detail": "Both lat and lng are required together"
    }
    assert lng_only_response.status_code == 400
    assert lng_only_response.json() == {
        "detail": "Both lat and lng are required together"
    }


def test_search_listings_with_lat_lng_calls_combined_search(monkeypatch):
    app = create_app(background_jobs_enabled=False)
    app.dependency_overrides[get_db] = _override_get_db
    captured = {}

    def fake_search_listings_combined(db, q, lat, lng, radius_km, limit):
        captured.update(
            {
                "db": db,
                "q": q,
                "lat": lat,
                "lng": lng,
                "radius_km": radius_km,
                "limit": limit,
            }
        )
        return [{"id": "listing-1"}]

    monkeypatch.setattr(
        listings_router_module,
        "search_listings_combined",
        fake_search_listings_combined,
    )

    with TestClient(app) as client:
        response = client.get(
            "/api/listings/search",
            params={
                "q": "beach",
                "lat": 13.1939,
                "lng": -59.5432,
                "radius_km": 15,
                "limit": 5,
            },
        )

    assert response.status_code == 200
    assert response.json() == [{"id": "listing-1"}]
    assert captured["q"] == "beach"
    assert captured["lat"] == 13.1939
    assert captured["lng"] == -59.5432
    assert captured["radius_km"] == 15.0
    assert captured["limit"] == 5
