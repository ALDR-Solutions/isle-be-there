from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape, from_shape
from typing import Optional
from fastapi import HTTPException
from shapely import Point

def extract_lat_lng(location) -> Optional[dict]:
    if isinstance(location, WKBElement):
        point = to_shape(location)
        return {"lat": float(point.y), "lng": float(point.x)}
    return None

def build_location(location_data):
    if not location_data:
        return None

    try:
        if isinstance(location_data, dict):
            lat = float(location_data.get("lat"))
            lng = float(location_data.get("lng"))
        else:
            # Pydantic object
            lat = float(location_data.lat)
            lng = float(location_data.lng)

    except (AttributeError, TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid location payload")

    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="lat and lng are required")

    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise HTTPException(status_code=400, detail="Location coordinates are out of range")

    return from_shape(Point(lng, lat), srid=4326)