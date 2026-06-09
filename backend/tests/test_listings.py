from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.infrastructure.database.engine import get_engine
from app.modules.listings.service import list_listings


def test_list_listings_from_country():
    country = "Barbados"

    with Session(get_engine()) as db:
        listings = list_listings(db=db, skip=0, limit=10, country=country)

    assert isinstance(listings, list)
    for listing in listings:
        assert listing["address"]["country"] == country


def test_search_listings_requires_lat_and_lng_together():
    with TestClient(app) as client:
        lat_only_response = client.get("/api/listings/search", params={"lat": 13.1939})
        lng_only_response = client.get("/api/listings/search", params={"lng": -59.5432})
        lat_lng_response = client.get("/api/listings/search", params={"lat": 13.1939, "lng": -59.5432})

    assert lat_only_response.status_code == 400
    assert lat_only_response.json() == {"detail": "Both lat and lng are required together"}

    assert lng_only_response.status_code == 400
    assert lng_only_response.json() == {"detail": "Both lat and lng are required together"}
    
    assert lat_lng_response.status_code == 200
    assert isinstance(lat_lng_response.json(), list)
