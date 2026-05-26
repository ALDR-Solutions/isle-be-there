from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import logging
from math import atan2, cos, radians, sin, sqrt
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.config import settings
from app.core.email import send_itinerary_email
from app.modules.bookings.schemas import BookingCreate
from app.modules.bookings.service import create_booking as booking_service_create
from app.modules.discounts.service import (
    check_package_discount_eligibility,
)
from app.modules.interests.models import Interests, UserInterest
from app.modules.listings.models import Listing, Statuses
from app.modules.listings.schemas import ListingLocation
from app.modules.listings.service import filter_by_availability, extract_lat_lng
from app.modules.services.models import Service, StatusTypes as ServiceStatusTypes
from app.modules.users.models import User

from .models import (
    Itinerary,
    ItineraryItem,
    ItineraryItemStatus,
    ItineraryStatus as ItineraryModelStatus,
)
from .schemas import (
    BudgetLevel,
    ItineraryDay,
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItinerarySaveRequest,
    ItineraryStatus as ItinerarySchemaStatus,
    ItineraryStop,
    ItineraryUnsavedEmailRequest,
    PaceLevel,
    SavedItineraryResponse,
    SavedItinerarySummaryResponse,
)

DEFAULT_DAY_START_HOUR = 9.0
DEFAULT_DAY_END_HOUR = 19.0
DEFAULT_MAX_TRAVEL_KM_BETWEEN_STOPS = 25.0
DEFAULT_LIMIT_CANDIDATES = 120

# Business types selected once for the whole trip, not greedily per day
ANCHOR_TYPES = {"hotel"}
REPEATABLE_TYPES = {"restaurant"}
HOTEL_CHECKIN_DURATION_HOURS = 1.0
HOTEL_STAY_DURATION_HOURS = 0.0

logger = logging.getLogger(__name__)


@dataclass
class Candidate:
    listing: Listing
    location: Optional[ListingLocation]
    business_type_name: str
    estimated_cost: float
    estimated_duration_hours: float
    interest_names: set[str]


def plan_itinerary(db: Session, request: ItineraryPlanRequest, user_id: Optional[UUID] = None) -> ItineraryPlanResponse:
    resolved_interests = resolve_interests(db, request.interests, user_id)
    if resolved_interests != set(request.interests or []):
        request = request.model_copy(update={"interests": list(resolved_interests)})
    all_candidates = load_candidates(db, request)
    days = request.resolved_trip_days
    resolved_daily_budget_target = daily_budget_target(request)
    resolved_hotel_nights = hotel_nights(request)

    hotel_candidate = pick_hotel(all_candidates, request) if all_candidates else None
    used_listing_ids: set = {hotel_candidate.listing.id} if hotel_candidate else set()
    activity_candidates = [
        c for c in all_candidates if c.business_type_name not in ANCHOR_TYPES
    ]

    day_rows = [
        schedule_day(
            day_idx=i,
            request=request,
            activity_candidates=activity_candidates,
            hotel_candidate=hotel_candidate,
            used_listing_ids=used_listing_ids,
            slots_per_day=slots_per_day(request.pace),
            daily_budget_target=resolved_daily_budget_target,
            hotel_nights=resolved_hotel_nights,
        )
        for i in range(days)
    ]

    return ItineraryPlanResponse(
        trip_days=days,
        budget_level=request.budget_level,
        pace=request.pace,
        total_estimated_cost=round(sum(d.total_estimated_cost for d in day_rows), 2),
        target_total_budget=None,
        daily_target_budget=round(resolved_daily_budget_target, 2),
        days=day_rows,
    )


def pick_hotel(
    candidates: list[Candidate], request: ItineraryPlanRequest
) -> Optional[Candidate]:
    """
    Select the single best hotel for the whole trip.
    Scored independently of day-level logic — proximity and variety don't apply here.
    """
    if hotel_nights(request) == 0:
        return None

    hotel_candidates = [c for c in candidates if c.business_type_name == "hotel"]
    if not hotel_candidates:
        return None

    best: Optional[Candidate] = None
    best_score = -10_000.0

    for candidate in hotel_candidates:
        score = 0.0

        # Budget fit
        score += budget_score(candidate.estimated_cost, request.budget_level)

        # Interest match by listing interest names
        if request.interests:
            matched = set(request.interests) & candidate.interest_names
            score += 10 * len(matched)

        if score > best_score:
            best_score = score
            best = candidate

    return best


def make_stop(
    candidate: Candidate,
    current_hour: float,
    best_score: float,
    reasons: list[str],
    estimated_cost: Optional[float] = None,
    estimated_duration_hours: Optional[float] = None,
) -> ItineraryStop:
    resolved_cost = (
        candidate.estimated_cost if estimated_cost is None else estimated_cost
    )
    resolved_duration = (
        candidate.estimated_duration_hours
        if estimated_duration_hours is None
        else estimated_duration_hours
    )
    end_hour = current_hour + resolved_duration
    return ItineraryStop(
        listing_id=candidate.listing.id,
        title=candidate.listing.title,
        description=candidate.listing.description,
        business_type_name=candidate.business_type_name,
        address=candidate.listing.address,
        estimated_cost=round(resolved_cost, 2),
        estimated_duration_hours=round(resolved_duration, 2),
        start_time=format_hour(current_hour),
        end_time=format_hour(end_hour),
        score=round(best_score, 2),
        reason_tags=reasons,
    )


# ---------------------------------------------------------------------------
# Persistence helpers (unchanged)
# ---------------------------------------------------------------------------


def list_saved_itineraries(
    db: Session, user_id: UUID
) -> list[SavedItinerarySummaryResponse]:
    itineraries = db.exec(
        select(Itinerary)
        .where(Itinerary.user_id == user_id)
        .order_by(desc(Itinerary.created_at))
    ).all()

    if not itineraries:
        return []

    itinerary_ids = [itinerary.id for itinerary in itineraries]
    item_rows = db.exec(
        select(ItineraryItem).where(
            ItineraryItem.__table__.c.itinerary_id.in_(itinerary_ids)
        )
    ).all()

    item_counts: dict[UUID, int] = {itinerary_id: 0 for itinerary_id in itinerary_ids}
    for item in item_rows:
        item_counts[item.itinerary_id] = item_counts.get(item.itinerary_id, 0) + 1

    return [
        SavedItinerarySummaryResponse(
            id=itinerary.id,
            title=itinerary.title,
            status=ItinerarySchemaStatus(status_value(itinerary.status)),
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            total_estimated_cost=float(itinerary.total_estimated_cost or 0),
            item_count=item_counts.get(itinerary.id, 0),
            created_at=itinerary.created_at,
        )
        for itinerary in itineraries
    ]


def get_saved_itinerary(
    db: Session, user_id: UUID, itinerary_id: UUID
) -> SavedItineraryResponse:
    itinerary = db.exec(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id)
        .where(Itinerary.user_id == user_id)
    ).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    items = db.exec(
        select(ItineraryItem)
        .where(ItineraryItem.itinerary_id == itinerary.id)
        .order_by(
            ItineraryItem.day_date, ItineraryItem.sort_order, ItineraryItem.start_at
        )
    ).all()

    return serialize_saved_itinerary(itinerary, items)


def save_itinerary(
    db: Session,
    user_id: UUID,
    payload: ItinerarySaveRequest,
) -> SavedItineraryResponse:
    planned = plan_itinerary(db, payload.plan_request, user_id)
    if len(planned.days) != payload.plan_request.resolved_trip_days:
        raise HTTPException(
            status_code=400,
            detail="Saved itinerary does not match requested trip length",
        )

    try:
        itinerary = Itinerary(
            user_id=user_id,
            title=resolved_title(payload),
            start_date=payload.plan_request.start_date,
            end_date=resolved_end_date(payload.plan_request),
            status=payload.status.value,
            budget_level=payload.plan_request.budget_level.value,
            pace=payload.plan_request.pace.value,
            country=payload.plan_request.country,
            interests=payload.plan_request.interests,
            total_estimated_cost=float(planned.total_estimated_cost),
        )
        db.add(itinerary)
        db.flush()

        items = build_items_for_saved_itinerary(itinerary.id, planned)
        for item in items:
            db.add(item)

        db.commit()
        db.refresh(itinerary)
        saved_items = db.exec(
            select(ItineraryItem)
            .where(ItineraryItem.itinerary_id == itinerary.id)
            .order_by(
                ItineraryItem.day_date, ItineraryItem.sort_order, ItineraryItem.start_at
            )
        ).all()
    except Exception:
        db.rollback()
        raise

    return serialize_saved_itinerary(itinerary, saved_items)


def delete_saved_itinerary(db: Session, user_id: UUID, itinerary_id: UUID) -> None:
    itinerary = db.exec(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id)
        .where(Itinerary.user_id == user_id)
    ).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    try:
        db.delete(itinerary)
        db.commit()
    except Exception:
        db.rollback()
        raise


def send_saved_itinerary_email(
    db: Session,
    user_id: UUID,
    itinerary_id: UUID,
    recipient_email: Optional[str] = None,
) -> str:
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    saved_itinerary = get_saved_itinerary(db, user_id, itinerary_id)
    itinerary_preview = saved_itinerary_to_plan_response(saved_itinerary)
    resolved_email = recipient_email or user.email
    if not resolved_email:
        raise HTTPException(status_code=400, detail="Recipient email is required")

    view_url = f"{settings.FRONTEND_URL}/itinerary/{saved_itinerary.id}"

    try:
        send_itinerary_email(
            resolved_email,
            saved_itinerary.title,
            itinerary_preview,
            country=saved_itinerary.country,
            interests=saved_itinerary.interests,
            view_url=view_url,
        )
    except Exception:
        logger.exception(
            "Failed to send itinerary %s to %s",
            saved_itinerary.id,
            resolved_email,
        )
        raise HTTPException(status_code=502, detail="Failed to send itinerary email")

    return resolved_email


def send_unsaved_itinerary_email(
    db: Session,
    user_id: Optional[UUID],
    payload: ItineraryUnsavedEmailRequest,
) -> str:
    user = None
    if user_id:
        user = db.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    resolved_email = payload.email or (user.email if user else None)
    if not resolved_email:
        raise HTTPException(status_code=400, detail="Recipient email is required")

    itinerary_preview = payload.plan_response or plan_itinerary(
        db,
        payload.plan_request,
        user_id,
    )
    if itinerary_preview.trip_days != payload.plan_request.resolved_trip_days:
        raise HTTPException(
            status_code=400,
            detail="Unsaved itinerary does not match requested trip length",
        )

    itinerary_title = resolved_unsaved_title(payload)

    try:
        send_itinerary_email(
            resolved_email,
            itinerary_title,
            itinerary_preview,
            country=payload.plan_request.country,
            interests=payload.plan_request.interests,
        )
    except Exception:
        logger.exception(
            "Failed to send unsaved itinerary to %s",
            resolved_email,
        )
        raise HTTPException(status_code=502, detail="Failed to send itinerary email")

    return resolved_email


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def load_candidates(db: Session, request: ItineraryPlanRequest) -> list[Candidate]:
    query = (
        select(Listing)
        .where(Listing.status.in_((Statuses.active, Statuses.approved)))
        .options(
            selectinload(Listing.business_type_rel), selectinload(Listing.interests)
        )
        .order_by(Listing.created_at.desc(), Listing.id)
    )

    if request.country:
        query = query.where(
            Listing.address["country"].astext.ilike(f"%{request.country}%")
        )

    if request.bookable_only:
        query = (
            query.join(Service, Service.listing_id == Listing.id)
            .where(Service.status == ServiceStatusTypes.active)
            .distinct()
        )

    rows = db.exec(query.limit(DEFAULT_LIMIT_CANDIDATES)).all()
    if not rows:
        return []

    if request.bookable_only:
        start_dt = datetime.combine(request.start_date, time.min)
        end_dt = datetime.combine(
            resolved_end_date(request) + timedelta(days=1), time.min
        )
        rows = filter_by_availability(db, rows, start_dt, end_dt)

    return [to_candidate(listing, request.budget_level) for listing in rows]


def hotel_nights(request: ItineraryPlanRequest) -> int:
    return max(request.resolved_trip_days - 1, 0)


def to_candidate(listing: Listing, budget_level: BudgetLevel) -> Candidate:
    business_type_name = (
        listing.business_type_rel.name if listing.business_type_rel else "unknown"
    ).lower()
    location = extract_lat_lng(listing.location)
    return Candidate(
        listing=listing,
        location=ListingLocation(**location) if location is not None else None,
        business_type_name=business_type_name,
        estimated_cost=estimate_cost(listing, business_type_name, budget_level),
        estimated_duration_hours=estimate_duration_hours(listing, business_type_name),
        interest_names={
            (interest.name or "").strip().lower()
            for interest in (listing.interests or [])
            if (interest.name or "").strip()
        },
    )


def score_candidate(
    candidate: Candidate,
    request: ItineraryPlanRequest,
    type_counts: dict[str, int],
    previous: Optional[Candidate],
    remaining_budget: float,
) -> tuple[float, list[str]]:
    score = 50.0
    reasons: list[str] = []

    if request.interests:
        matched = set(request.interests) & candidate.interest_names
        if matched:
            score += 12 * len(matched)
            reasons.append("interest_match")
        else:
            score -= 2

    repeated_type_count = type_counts.get(candidate.business_type_name, 0)
    if repeated_type_count:
        score -= 8 * repeated_type_count
    else:
        score += 5
        reasons.append("variety")

    score += budget_score(candidate.estimated_cost, request.budget_level)
    if candidate.estimated_cost <= remaining_budget:
        score += 6
        reasons.append("within_budget")
    else:
        score -= 10

    # ✓ Guard both locations before dereferencing
    prev_loc = previous.location if previous else None
    cand_loc = candidate.location
    if prev_loc is not None and cand_loc is not None:
        distance_km = haversine_km(
            prev_loc.lat,
            prev_loc.lng,
            cand_loc.lat,
            cand_loc.lng,
        )
        if distance_km <= DEFAULT_MAX_TRAVEL_KM_BETWEEN_STOPS:
            score += 8
            reasons.append("near_previous_stop")
        elif distance_km > DEFAULT_MAX_TRAVEL_KM_BETWEEN_STOPS * 1.5:
            score -= 20

    return score, reasons


def schedule_day(
    day_idx: int,
    request: ItineraryPlanRequest,
    activity_candidates: list[Candidate],
    hotel_candidate: Optional[Candidate],
    used_listing_ids: set,
    slots_per_day: int,
    daily_budget_target: float,
    hotel_nights: int,
) -> ItineraryDay:
    current_date = day_at(request.start_date, day_idx)
    day_stops: list[ItineraryStop] = []
    day_used_listing_ids: set[UUID] = set()
    type_counts: dict[str, int] = {}
    remaining_budget = daily_budget_target
    current_hour = DEFAULT_DAY_START_HOUR
    previous: Optional[Candidate] = None
    scheduled_activity_count = 0

    if hotel_candidate is not None and day_idx < hotel_nights:
        hotel_duration = (
            HOTEL_CHECKIN_DURATION_HOURS if day_idx == 0 else HOTEL_STAY_DURATION_HOURS
        )
        hotel_stop = make_stop(
            hotel_candidate,
            current_hour,
            best_score=100.0,
            reasons=["hotel_checkin" if day_idx == 0 else "hotel_stay"],
            estimated_cost=hotel_candidate.estimated_cost,
            estimated_duration_hours=hotel_duration,
        )
        day_stops.append(hotel_stop)
        used_listing_ids.add(hotel_candidate.listing.id)
        day_used_listing_ids.add(hotel_candidate.listing.id)
        remaining_budget = max(0.0, remaining_budget - hotel_stop.estimated_cost)
        if hotel_duration > 0:
            current_hour += hotel_duration + 0.5
            previous = hotel_candidate
        type_counts["hotel"] = 1

    while scheduled_activity_count < slots_per_day:
        best_candidate, best_score, best_reasons = pick_best_activity(
            activity_candidates=activity_candidates,
            day_used_listing_ids=day_used_listing_ids,
            used_listing_ids=used_listing_ids,
            current_hour=current_hour,
            type_counts=type_counts,
            previous=previous,
            remaining_budget=remaining_budget,
            request=request,
        )
        if best_candidate is None:
            break

        stop = make_stop(best_candidate, current_hour, best_score, best_reasons)
        day_stops.append(stop)
        scheduled_activity_count += 1
        day_used_listing_ids.add(best_candidate.listing.id)
        if best_candidate.business_type_name not in REPEATABLE_TYPES:
            used_listing_ids.add(best_candidate.listing.id)

        current_hour += best_candidate.estimated_duration_hours + 0.5
        remaining_budget = max(0.0, remaining_budget - best_candidate.estimated_cost)
        previous = best_candidate
        type_counts[best_candidate.business_type_name] = (
            type_counts.get(best_candidate.business_type_name, 0) + 1
        )

    return ItineraryDay(
        date=current_date,
        total_estimated_cost=round(sum(s.estimated_cost for s in day_stops), 2),
        total_duration_hours=round(
            sum(s.estimated_duration_hours for s in day_stops), 2
        ),
        stops=day_stops,
    )


def pick_best_activity(
    activity_candidates: list[Candidate],
    day_used_listing_ids: set[UUID],
    used_listing_ids: set,
    current_hour: float,
    type_counts: dict[str, int],
    previous: Optional[Candidate],
    remaining_budget: float,
    request: ItineraryPlanRequest,
) -> tuple[Optional[Candidate], float, list[str]]:
    best_candidate: Optional[Candidate] = None
    best_score = -10_000.0
    best_reasons: list[str] = []

    for candidate in activity_candidates:
        if candidate.listing.id in day_used_listing_ids:
            continue
        if (
            candidate.listing.id in used_listing_ids
            and candidate.business_type_name not in REPEATABLE_TYPES
        ):
            continue
        if current_hour + candidate.estimated_duration_hours > DEFAULT_DAY_END_HOUR:
            continue

        score, reasons = score_candidate(
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

    return best_candidate, best_score, best_reasons


def budget_score(cost: float, budget_level: BudgetLevel) -> float:
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
    # BudgetLevel.high — reward pricier options
    if cost <= 260:
        return 8
    return 14


def estimate_cost(
    listing: Listing, business_type_name: str, budget_level: BudgetLevel
) -> float:
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


def estimate_duration_hours(listing: Listing, business_type_name: str) -> float:
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


def slots_per_day(pace: PaceLevel) -> int:
    if pace == PaceLevel.relaxed:
        return 2
    if pace == PaceLevel.packed:
        return 4
    return 3


def daily_budget_target(request: ItineraryPlanRequest) -> float:
    defaults = {
        BudgetLevel.low: 120.0,
        BudgetLevel.medium: 240.0,
        BudgetLevel.high: 420.0,
    }
    return defaults[request.budget_level]


def day_at(start_date: date, idx: int) -> date:
    return start_date + timedelta(days=idx)


def format_hour(hour_value: float) -> str:
    total_minutes = int(round(hour_value * 60))
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    return f"{hours:02d}:{minutes:02d}"


def parse_hour_value(hour_value: str) -> time:
    try:
        hour_part, minute_part = hour_value.split(":", maxsplit=1)
        parsed_hour = int(hour_part)
        parsed_minute = int(minute_part)
    except (AttributeError, ValueError) as exc:
        raise HTTPException(
            status_code=400, detail="Invalid itinerary stop time format"
        ) from exc

    return time(hour=parsed_hour, minute=parsed_minute)


def resolved_end_date(request: ItineraryPlanRequest) -> date:
    if request.end_date is not None:
        return request.end_date
    return day_at(request.start_date, request.resolved_trip_days - 1)


def resolved_title(payload: ItinerarySaveRequest) -> str:
    if payload.title and payload.title.strip():
        return payload.title.strip()

    location = payload.plan_request.country or "Trip"
    return f"{location} itinerary"


def resolved_unsaved_title(payload: ItineraryUnsavedEmailRequest) -> str:
    if payload.title and payload.title.strip():
        return payload.title.strip()

    location = payload.plan_request.country or "Trip"
    return f"{location} itinerary"


def build_items_for_saved_itinerary(
    itinerary_id: UUID,
    planned: ItineraryPlanResponse,
) -> list[ItineraryItem]:
    items: list[ItineraryItem] = []

    for day_index, day in enumerate(planned.days):
        for stop_index, stop in enumerate(day.stops):
            start_at = datetime.combine(day.date, parse_hour_value(stop.start_time))
            end_at = datetime.combine(day.date, parse_hour_value(stop.end_time))
            items.append(
                ItineraryItem(
                    itinerary_id=itinerary_id,
                    listing_id=stop.listing_id,
                    item_type="stop",
                    title=stop.title,
                    description=stop.description,
                    day_date=day.date,
                    start_at=start_at,
                    end_at=end_at,
                    sort_order=(day_index * 100) + stop_index,
                    estimated_cost=float(stop.estimated_cost),
                    address_snapshot=stop.address,
                    reason_tags=stop.reason_tags,
                    extra_metadata={
                        "score": stop.score,
                        "business_type_name": stop.business_type_name,
                        "estimated_duration_hours": stop.estimated_duration_hours,
                    },
                )
            )

    return items


def status_value(status) -> str:
    return status.value if hasattr(status, "value") else str(status)


def serialize_saved_itinerary(
    itinerary: Itinerary,
    items: list[ItineraryItem],
) -> SavedItineraryResponse:
    return SavedItineraryResponse(
        id=itinerary.id,
        user_id=itinerary.user_id,
        title=itinerary.title,
        status=ItinerarySchemaStatus(status_value(itinerary.status)),
        start_date=itinerary.start_date,
        end_date=itinerary.end_date,
        budget_level=BudgetLevel(itinerary.budget_level),
        pace=PaceLevel(itinerary.pace),
        country=itinerary.country,
        interests=list(itinerary.interests or []),
        total_estimated_cost=float(itinerary.total_estimated_cost or 0),
        created_at=itinerary.created_at,
        updated_at=itinerary.updated_at,
        items=[
            {
                "id": item.id,
                "itinerary_id": item.itinerary_id,
                "listing_id": item.listing_id,
                "linked_booking_id": item.linked_booking_id,
                "item_type": item.item_type,
                "title": item.title,
                "description": item.description,
                "day_date": item.day_date,
                "start_at": item.start_at,
                "end_at": item.end_at,
                "sort_order": item.sort_order,
                "estimated_cost": float(item.estimated_cost or 0),
                "address_snapshot": item.address_snapshot,
                "reason_tags": list(item.reason_tags or []),
                "extra_metadata": item.extra_metadata,
            }
            for item in items
        ],
    )


def saved_itinerary_to_plan_response(
    saved_itinerary: SavedItineraryResponse,
) -> ItineraryPlanResponse:
    grouped_days: dict[date, dict] = {}

    for item in saved_itinerary.items or []:
        day_date = item_value(item, "day_date")
        if day_date is None:
            continue

        grouped_day = grouped_days.setdefault(
            day_date,
            {
                "date": day_date,
                "total_estimated_cost": 0.0,
                "total_duration_hours": 0.0,
                "stops": [],
            },
        )

        estimated_cost = float(item_value(item, "estimated_cost", 0.0) or 0.0)
        extra_metadata = item_value(item, "extra_metadata", {}) or {}
        estimated_duration = float(
            dict_or_attr_value(extra_metadata, "estimated_duration_hours", 0.0) or 0.0
        )
        grouped_day["stops"].append(
            ItineraryStop(
                listing_id=item_value(item, "listing_id") or item_value(item, "id"),
                title=item_value(item, "title", ""),
                description=item_value(item, "description"),
                business_type_name=dict_or_attr_value(
                    extra_metadata,
                    "business_type_name",
                    item_value(item, "item_type", "stop"),
                ),
                address=item_value(item, "address_snapshot", {}) or {},
                estimated_cost=estimated_cost,
                estimated_duration_hours=estimated_duration,
                start_time=format_datetime_time(item_value(item, "start_at")),
                end_time=format_datetime_time(item_value(item, "end_at")),
                score=float(dict_or_attr_value(extra_metadata, "score", 0.0) or 0.0),
                reason_tags=list(item_value(item, "reason_tags", []) or []),
            )
        )
        grouped_day["total_estimated_cost"] += estimated_cost
        grouped_day["total_duration_hours"] += estimated_duration

    days = [
        ItineraryDay(
            date=day["date"],
            total_estimated_cost=round(day["total_estimated_cost"], 2),
            total_duration_hours=round(day["total_duration_hours"], 2),
            stops=day["stops"],
        )
        for _, day in sorted(grouped_days.items(), key=lambda row: row[0])
    ]

    total_estimated_cost = float(saved_itinerary.total_estimated_cost or 0.0)
    daily_target_budget = (
        round(total_estimated_cost / len(days), 2) if days else 0.0
    )

    return ItineraryPlanResponse(
        trip_days=len(days),
        budget_level=saved_itinerary.budget_level,
        pace=saved_itinerary.pace,
        total_estimated_cost=round(total_estimated_cost, 2),
        target_total_budget=saved_itinerary.total_budget,
        daily_target_budget=daily_target_budget,
        days=days,
    )


def item_value(item, key: str, default=None):
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def dict_or_attr_value(value, key: str, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def format_datetime_time(value) -> str:
    if isinstance(value, datetime):
        return value.strftime("%H:%M")
    if isinstance(value, str) and len(value) >= 16:
        return value[11:16]
    return ""


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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
        status=ItineraryModelStatus.DRAFT,
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

    if itinerary.status != ItineraryModelStatus.DRAFT:
        raise HTTPException(
            status_code=400, detail="Only DRAFT itineraries can be confirmed"
        )

    discount_info = check_package_discount_eligibility(db, itinerary)
    discount_applied = False
    discount_amount = 0.0

    if discount_info.get("eligible"):
        discount = discount_info["discount"]
        discount_amount = discount_info.get("estimated_discount", 0)
        itinerary.applied_discount_id = discount.id
        itinerary.discount_amount = discount_amount
        discount_applied = True

    itinerary.status = ItineraryModelStatus.CONFIRMED
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

    if itinerary.status != ItineraryModelStatus.CONFIRMED:
        raise HTTPException(
            status_code=400,
            detail="Only CONFIRMED itineraries can be converted to bookings",
        )

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
        itinerary.status = ItineraryModelStatus.COMPLETED

    db.commit()
    db.refresh(itinerary)
    return itinerary

def resolve_interests(
    db: Session,
    request_interests: list[str] | None,
    user_id: Optional[UUID],
) -> set[str]:
    combined = {
        interest.strip().lower()
        for interest in (request_interests or [])
        if interest and interest.strip()
    }

    if user_id:
        user_interest_names = db.exec(
            select(Interests.name)
            .join(UserInterest, UserInterest.interest_id == Interests.id)
            .where(UserInterest.user_id == user_id)
        ).all()
        combined |= {
            (name or "").strip().lower()
            for name in user_interest_names
            if (name or "").strip()
        }

    return combined
