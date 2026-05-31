"""Shared domain helpers for repeated lookup and authorization rules."""

from .context import (
    get_business_employee_link_or_404,
    get_employee_business_link_or_404,
    get_listing_for_business_or_404,
    get_owned_business_or_404,
    get_owned_itinerary_item_context_or_404,
    get_owned_itinerary_or_404,
)
from .lookups import (
    get_booking_or_404,
    get_business_by_user_id,
    get_business_or_404,
    get_itinerary_item_or_404,
    get_itinerary_or_404,
    get_listing_or_404,
    get_review_or_404,
    get_service_or_404,
    get_user_by_id,
    get_user_or_404,
)
from .ownership import (
    ensure_booking_owner,
    ensure_business_owner,
    ensure_itinerary_owner,
    ensure_listing_belongs_to_business,
    ensure_listing_owner,
    ensure_review_owner,
    ensure_service_access,
    is_admin_user,
)

__all__ = [
    "ensure_booking_owner",
    "ensure_business_owner",
    "ensure_itinerary_owner",
    "ensure_listing_belongs_to_business",
    "ensure_listing_owner",
    "ensure_review_owner",
    "ensure_service_access",
    "get_booking_or_404",
    "get_business_by_user_id",
    "get_business_employee_link_or_404",
    "get_business_or_404",
    "get_employee_business_link_or_404",
    "get_itinerary_item_or_404",
    "get_itinerary_or_404",
    "get_listing_for_business_or_404",
    "get_listing_or_404",
    "get_owned_business_or_404",
    "get_owned_itinerary_item_context_or_404",
    "get_owned_itinerary_or_404",
    "get_review_or_404",
    "get_service_or_404",
    "get_user_by_id",
    "get_user_or_404",
    "is_admin_user",
]
