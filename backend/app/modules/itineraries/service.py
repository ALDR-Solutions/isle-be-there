"""Facade for itinerary module services."""

from .emailing import send_saved_itinerary_email, send_unsaved_itinerary_email
from .persistence import (
    confirm_itinerary,
    convert_itinerary_to_bookings,
    create_itinerary,
    delete_saved_itinerary,
    get_itinerary_by_id,
    get_saved_itinerary,
    list_saved_itineraries,
    save_itinerary,
)
from .planner import plan_itinerary, resolve_interests
from .serialization import (
    build_items_for_saved_itinerary,
    saved_itinerary_to_plan_response,
    serialize_saved_itinerary,
)

__all__ = [
    "build_items_for_saved_itinerary",
    "confirm_itinerary",
    "convert_itinerary_to_bookings",
    "create_itinerary",
    "delete_saved_itinerary",
    "get_itinerary_by_id",
    "get_saved_itinerary",
    "list_saved_itineraries",
    "plan_itinerary",
    "resolve_interests",
    "save_itinerary",
    "saved_itinerary_to_plan_response",
    "send_saved_itinerary_email",
    "send_unsaved_itinerary_email",
    "serialize_saved_itinerary",
]
