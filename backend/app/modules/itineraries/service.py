from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from math import atan2, cos, radians, sin, sqrt
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.service import create_booking as booking_service_create
from app.modules.discounts.models import Discount, DiscountType
from app.modules.discounts.service import check_package_discount_eligibility, get_or_create_package_discount as discount_get_or_create
from app.modules.listings.models import Listing, Statuses

from .models import Itinerary, ItineraryItem, ItineraryStatus, ItineraryItemStatus
from .schemas import (
    BudgetLevel,
    ItineraryDay,
    ItineraryItemCreate,
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItineraryStop,
    PaceLevel,
)


@dataclass
class Candidate:
    listing: Listing
    lat: Optional[float]
    lng: Optional[float]
    business_type_name: str
    estimated_cost: float
    estimated_duration_hours: float


def plan_itinerary(db: Session, request: ItineraryPlanRequest) -> ItineraryPlanResponse:
    candidates = _load_candidates(db, request)
    if not candidates:
        return ItineraryPlanResponse(
            trip_days=request.resolved_trip_days,
            budget_level=request.budget_level,
            pace=request.pace,
            total_estimated_cost=0,
            target_total_budget=request.total_budget,
            daily_target_budget=_daily_budget_target(request),
            days=[ItineraryDay(date=_day_at(request.start_date, i), total_estimated_cost=0, total_duration_hours=0) for i in range(request.resolved_trip_days)],
        )

    must_include = [c for c in candidates if c.listing.id in set(request.must_include_listing_ids)]
    optional = [c for c in candidates if c.listing.id not in set(request.must_include_listing_ids)]
    days = request.resolved_trip_days
    slots_per_day = _slots_per_day(request.pace, request.max_listings_per_day)
    daily_budget_target = _daily_budget_target(request)

    day_rows: list[ItineraryDay] = []
    used_listing_ids = set()

    must_by_day: list[list[Candidate]] = [[] for _ in range(days)]
    for idx, candidate in enumerate(must_include):
        must_by_day[idx % days].append(candidate)

    for day_idx in range(days):
        current_date = _day_at(request.start_date, day_idx)
        day_stops: list[ItineraryStop] = []
        type_counts: dict[str, int] = {}
        remaining_budget = daily_budget_target
        current_hour = float(request.day_start_hour)
        previous = None

        day_candidates = must_by_day[day_idx] + optional

        while len(day_stops) < slots_per_day:
            best_candidate = None
            best_score = -10_000.0
            best_reasons: list[str] = []

            for candidate in day_candidates:
                listing_id = candidate.listing.id
                if listing_id in used_listing_ids:
                    continue
                if listing_id in set(request.excluded_listing_ids):
                    continue

                if request.strict_budget and candidate.estimated_cost > remaining_budget and day_stops:
                    continue

                end_hour = current_hour + candidate.estimated_duration_hours
                if end_hour > request.day_end_hour:
                    continue

                score, reasons = _score_candidate(
                    candidate=candidate,
                    request=request,
                    type_counts=type_counts,
                    previous=previous,
                    remaining_budget=remaining_budget,
                )

                if score > best_score:
                    best_score = score
                    best_candidate = candidate
                    best_reasons = reasons

            if best_candidate is None:
                break

            end_hour = current_hour + best_candidate.estimated_duration_hours
            stop = ItineraryStop(
                listing_id=best_candidate.listing.id,
                title=best_candidate.listing.title,
                business_type_name=best_candidate.business_type_name,
                address=best_candidate.listing.address,
                estimated_cost=round(best_candidate.estimated_cost, 2),
                estimated_duration_hours=round(best_candidate.estimated_duration_hours, 2),
                start_time=_format_hour(current_hour),
                end_time=_format_hour(end_hour),
                score=round(best_score, 2),
                reason_tags=best_reasons,
            )
            day_stops.append(stop)
            used_listing_ids.add(best_candidate.listing.id)
            current_hour = end_hour + 0.5
            remaining_budget = max(0.0, remaining_budget - best_candidate.estimated_cost)
            previous = best_candidate
            type_counts[best_candidate.business_type_name] = type_counts.get(best_candidate.business_type_name, 0) + 1

        day_rows.append(
            ItineraryDay(
                date=current_date,
                total_estimated_cost=round(sum(s.estimated_cost for s in day_stops), 2),
                total_duration_hours=round(sum(s.estimated_duration_hours for s in day_stops), 2),
                stops=day_stops,
            )
        )

    return ItineraryPlanResponse(
        trip_days=days,
        budget_level=request.budget_level,
        pace=request.pace,
        total_estimated_cost=round(sum(day.total_estimated_cost for day in day_rows), 2),
        target_total_budget=request.total_budget,
        daily_target_budget=round(daily_budget_target, 2),
        days=day_rows,
    )


def _load_candidates(db: Session, request: ItineraryPlanRequest) -> list[Candidate]:
    query = (
        select(Listing)
        .where(Listing.status.in_((Statuses.active, Statuses.approved)))
        .options(selectinload(Listing.business_type_rel))
    )

    if request.city:
        query = query.where(Listing.address["city"].astext.ilike(f"%{request.city}%"))
    if request.country:
        query = query.where(Listing.address["country"].astext.ilike(f"%{request.country}%"))
    if request.excluded_listing_ids:
        query = query.where(Listing.__table__.c.id.notin_(request.excluded_listing_ids))

    rows = db.exec(query.limit(request.limit_candidates)).all()
    if not rows:
        return []

    candidate_list = [_to_candidate(listing, request.budget_level) for listing in rows]
    must_ids = set(request.must_include_listing_ids)
    if not must_ids:
        return candidate_list

    found_ids = {candidate.listing.id for candidate in candidate_list}
    missing = [str(value) for value in must_ids if value not in found_ids]
    if missing:
        raise HTTPException(status_code=404, detail=f"Must-include listings not found: {', '.join(missing)}")

    return candidate_list


def _to_candidate(listing: Listing, budget_level: BudgetLevel) -> Candidate:
    lat, lng = _extract_lat_lng(listing.location)
    business_type_name = (listing.business_type_rel.name if listing.business_type_rel else "unknown").lower()
    return Candidate(
        listing=listing,
        lat=lat,
        lng=lng,
        business_type_name=business_type_name,
        estimated_cost=_estimate_cost(listing, business_type_name, budget_level),
        estimated_duration_hours=_estimate_duration_hours(listing, business_type_name),
    )


def _score_candidate(
    candidate: Candidate,
    request: ItineraryPlanRequest,
    type_counts: dict[str, int],
    previous: Optional[Candidate],
    remaining_budget: float,
) -> tuple[float, list[str]]:
    score = 50.0
    reasons: list[str] = []

    if request.preferred_business_types:
        if candidate.business_type_name in request.preferred_business_types:
            score += 20
            reasons.append("preferred_type")
        else:
            score -= 4

    text_blob = f"{candidate.listing.title} {candidate.listing.description or ''}".lower()
    if request.interests:
        matches = sum(1 for interest in request.interests if interest in text_blob)
        if matches:
            score += 12 * matches
            reasons.append("interest_match")
        else:
            score -= 2

    repeated_type_count = type_counts.get(candidate.business_type_name, 0)
    if repeated_type_count:
        score -= 8 * repeated_type_count
    else:
        score += 5
        reasons.append("variety")

    score += _budget_score(candidate.estimated_cost, request.budget_level)
    if candidate.estimated_cost <= remaining_budget:
        score += 6
        reasons.append("within_budget")
    elif request.strict_budget:
        score -= 100

    if previous and all(v is not None for v in [previous.lat, previous.lng, candidate.lat, candidate.lng]):
        distance_km = _haversine_km(previous.lat, previous.lng, candidate.lat, candidate.lng)  # type: ignore[arg-type]
        if distance_km <= request.max_travel_km_between_stops:
            score += 8
            reasons.append("near_previous_stop")
        elif distance_km > request.max_travel_km_between_stops * 1.5:
            score -= 20

    return score, reasons


def _budget_score(cost: float, budget_level: BudgetLevel) -> float:
    if budget_level == BudgetLevel.low:
        if cost <= 50:
            return 16
        if cost <= 100:
            return 8
        return -10
    if budget_level == BudgetLevel.medium:
        if cost <= 160:
            return 12
        if cost <= 240:
            return 6
        return -6
    if cost <= 260:
        return 8
    return 14


def _estimate_cost(listing: Listing, business_type_name: str, budget_level: BudgetLevel) -> float:
    if listing.base_price is not None:
        return float(listing.base_price)

    defaults_by_type = {
        "hotel": 180.0,
        "tour": 90.0,
        "activity": 65.0,
        "restaurant": 45.0,
        "unknown": 75.0,
    }
    default_cost = defaults_by_type.get(business_type_name, defaults_by_type["unknown"])
    if budget_level == BudgetLevel.low:
        return default_cost * 0.8
    if budget_level == BudgetLevel.high:
        return default_cost * 1.25
    return default_cost


def _estimate_duration_hours(listing: Listing, business_type_name: str) -> float:
    details = listing.details or {}
    for key in ("estimated_duration", "duration"):
        value = details.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)

    defaults_by_type = {
        "hotel": 1.0,
        "tour": 3.0,
        "activity": 2.5,
        "restaurant": 1.5,
        "unknown": 2.0,
    }
    return defaults_by_type.get(business_type_name, 2.0)


def _extract_lat_lng(location) -> tuple[Optional[float], Optional[float]]:
    if isinstance(location, WKBElement):
        point = to_shape(location)
        return float(point.y), float(point.x)
    return None, None


def _slots_per_day(pace: PaceLevel, override: Optional[int]) -> int:
    if override is not None:
        return override
    if pace == PaceLevel.relaxed:
        return 2
    if pace == PaceLevel.packed:
        return 4
    return 3


def _daily_budget_target(request: ItineraryPlanRequest) -> float:
    if request.total_budget:
        return request.total_budget / request.resolved_trip_days

    defaults = {
        BudgetLevel.low: 120.0,
        BudgetLevel.medium: 240.0,
        BudgetLevel.high: 420.0,
    }
    return defaults[request.budget_level]


def _day_at(start_date: date, idx: int) -> date:
    return start_date + timedelta(days=idx)


def _format_hour(hour_value: float) -> str:
    total_minutes = int(round(hour_value * 60))
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius_km * c


def create_itinerary(db: Session, user_id: UUID, data: dict) -> Itinerary:
    """Create a new Itinerary with DRAFT status, create ItineraryItems, and calculate total_estimated_cost."""
    items_data = data.pop("items", [])
    total_cost = sum(item.get("estimated_cost", 0) for item in items_data)

    itinerary = Itinerary(
        user_id=user_id,
        status=ItineraryStatus.DRAFT,
        total_estimated_cost=total_cost,
        **data,
    )
    db.add(itinerary)
    db.flush()

    for item_data in items_data:
        item = ItineraryItem(
            itinerary_id=itinerary.id,
            status=ItineraryItemStatus.PLANNED,
            **item_data,
        )
        db.add(item)

    db.commit()
    db.refresh(itinerary)
    return itinerary


def get_itinerary_by_id(db: Session, itinerary_id: UUID, user_id: UUID) -> Itinerary:
    """Get an itinerary by ID with its items."""
    itinerary = db.exec(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id, Itinerary.user_id == user_id)
        .options(selectinload(Itinerary.items))
    ).first()

    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    return itinerary


def confirm_itinerary(db: Session, itinerary_id: UUID, user_id: UUID) -> dict:
    """Confirm a DRAFT itinerary, apply discount if eligible, update status to CONFIRMED."""
    itinerary = get_itinerary_by_id(db, itinerary_id, user_id)

    if itinerary.status != ItineraryStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only DRAFT itineraries can be confirmed")

    discount_info = check_package_discount_eligibility(db, itinerary)
    discount_applied = False
    discount_amount = 0.0

    if discount_info.get("eligible"):
        discount = discount_info["discount"]
        discount_amount = discount_info.get("estimated_discount", 0)
        itinerary.applied_discount_id = discount.id
        itinerary.discount_amount = discount_amount
        discount_applied = True

    itinerary.status = ItineraryStatus.CONFIRMED
    db.commit()
    db.refresh(itinerary)

    return {
        "itinerary": itinerary,
        "discount_applied": discount_applied,
        "discount_amount": discount_amount,
    }


def convert_itinerary_to_bookings(
    db: Session,
    itinerary_id: UUID,
    user_id: UUID,
    item_ids: list[UUID] | None = None,
) -> Itinerary:
    """Convert a confirmed itinerary's items to bookings."""
    itinerary = get_itinerary_by_id(db, itinerary_id, user_id)

    if itinerary.status != ItineraryStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Only CONFIRMED itineraries can be converted to bookings")

    items = itinerary.items
    if item_ids is not None:
        items = [item for item in items if item.id in item_ids]

    all_booked = True
    for item in items:
        if item.linked_booking_id is not None:
            continue

        booking_data = BookingCreate(
            listing_id=item.listing_id,
            itinerary_id=itinerary_id,
            itinerary_item_id=item.id,
            booking_from_time=item.start_at,
            booking_to_time=item.end_at,
        )
        booking = booking_service_create(db, booking_data, user_id)

        item.linked_booking_id = booking.id
        item.status = ItineraryItemStatus.BOOKED
        db.add(item)

        if booking.status.value == "cancelled":
            all_booked = False

    if all_booked and items:
        itinerary.status = ItineraryStatus.COMPLETED

    db.commit()
    db.refresh(itinerary)
    return itinerary


# ---------------------------------------------------------------------------
# Discount helpers (fallback implementations until DiscountService exists)
# ---------------------------------------------------------------------------


def get_or_create_package_discount(db: Session) -> Discount:
    """Get active package discount, create default if none exists."""
    now = datetime.utcnow()
    discount = db.exec(
        select(Discount)
        .where(
            Discount.discount_type == DiscountType.PACKAGE,
            Discount.is_active == True,
            Discount.valid_from <= now,
            (Discount.valid_to == None) | (Discount.valid_to >= now),
        )
        .order_by(Discount.created_at.desc())
        .limit(1)
    ).first()

    if discount:
        return discount

    # Create default package discount
    default_discount = Discount(
        name="Package Discount",
        discount_type=DiscountType.PACKAGE,
        discount_percent=0.10,
        min_services=3,
        min_total_cost=100.0,
        is_active=True,
        valid_from=now,
        max_uses=1000,
        description="Default package discount for booking 3+ services",
    )
    db.add(default_discount)
    db.commit()
    db.refresh(default_discount)
    return default_discount


def check_package_discount_eligibility(db: Session, itinerary: Itinerary) -> dict:
    """Check if an itinerary is eligible for a package discount."""
    discount = get_or_create_package_discount(db)

    item_count = len(itinerary.items) if itinerary.items else 0
    total_cost = itinerary.total_estimated_cost or 0

    eligible = True
    reason = None
    estimated_discount = 0.0

    if discount.min_services and item_count < discount.min_services:
        eligible = False
        reason = f"Requires at least {discount.min_services} services, have {item_count}"
    elif discount.min_total_cost and total_cost < discount.min_total_cost:
        eligible = False
        reason = f"Minimum total cost {discount.min_total_cost} required"
    elif not discount.is_active:
        eligible = False
        reason = "Discount is not active"

    if eligible and discount.discount_percent:
        estimated_discount = min(
            total_cost * discount.discount_percent,
            discount.max_discount_amount or float("inf"),
        )

    return {
        "discount": discount,
        "eligible": eligible,
        "reason": reason,
        "estimated_discount": estimated_discount,
    }

