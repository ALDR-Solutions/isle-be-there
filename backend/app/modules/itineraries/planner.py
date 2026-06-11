from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from math import atan2, cos, radians, sin, sqrt
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.modules.interests.models import Interests, UserInterest
from app.modules.listings.models import Listing, Statuses
from app.modules.listings.service import filter_by_availability
from app.modules.services.models import Service, StatusTypes as ServiceStatusTypes
from app.shared.schemas import Location
from app.shared.services import extract_lat_lng

from .schemas import (
    BudgetLevel,
    ItineraryDay,
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItineraryStop,
    PaceLevel,
)

DEFAULT_DAY_START_HOUR = 9.0
DEFAULT_DAY_END_HOUR = 19.0
DEFAULT_MAX_TRAVEL_KM_BETWEEN_STOPS = 25.0
DEFAULT_LIMIT_CANDIDATES = 120

ANCHOR_TYPES = {"hotel"}
REPEATABLE_TYPES = {"restaurant"}
HOTEL_CHECKIN_DURATION_HOURS = 1.0
HOTEL_STAY_DURATION_HOURS = 0.0


@dataclass
class Candidate:
    listing: Listing
    location: Optional[Location]
    business_type_name: str
    estimated_cost: float
    estimated_duration_hours: float
    interest_names: set[str]


def plan_itinerary(
    db: Session,
    request: ItineraryPlanRequest,
    user_id: Optional[UUID] = None,
) -> ItineraryPlanResponse:
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
        candidate
        for candidate in all_candidates
        if candidate.business_type_name not in ANCHOR_TYPES
    ]

    day_rows = [
        schedule_day(
            day_idx=index,
            request=request,
            activity_candidates=activity_candidates,
            hotel_candidate=hotel_candidate,
            used_listing_ids=used_listing_ids,
            slots_per_day=slots_per_day(request.pace),
            daily_budget_target=resolved_daily_budget_target,
            hotel_nights=resolved_hotel_nights,
        )
        for index in range(days)
    ]

    return ItineraryPlanResponse(
        trip_days=days,
        budget_level=request.budget_level,
        pace=request.pace,
        total_estimated_cost=round(sum(day.total_estimated_cost for day in day_rows), 2),
        target_total_budget=None,
        daily_target_budget=round(resolved_daily_budget_target, 2),
        days=day_rows,
    )


def load_candidates(db: Session, request: ItineraryPlanRequest) -> list[Candidate]:
    query = (
        select(Listing)
        .where(Listing.status.in_((Statuses.active, Statuses.approved)))
        .options(
            selectinload(Listing.business_type_rel),
            selectinload(Listing.interests),
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
            resolved_end_date(request) + timedelta(days=1),
            time.min,
        )
        rows = filter_by_availability(db, rows, start_dt, end_dt)

    return [to_candidate(listing, request.budget_level) for listing in rows]


def pick_hotel(
    candidates: list[Candidate],
    request: ItineraryPlanRequest,
) -> Optional[Candidate]:
    if hotel_nights(request) == 0:
        return None

    hotel_candidates = [
        candidate for candidate in candidates if candidate.business_type_name == "hotel"
    ]
    if not hotel_candidates:
        return None

    best: Optional[Candidate] = None
    best_score = -10_000.0

    for candidate in hotel_candidates:
        score = budget_score(candidate.estimated_cost, request.budget_level)
        if request.interests:
            matched = set(request.interests) & candidate.interest_names
            score += 10 * len(matched)

        if score > best_score:
            best_score = score
            best = candidate

    return best


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
        total_estimated_cost=round(sum(stop.estimated_cost for stop in day_stops), 2),
        total_duration_hours=round(
            sum(stop.estimated_duration_hours for stop in day_stops),
            2,
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


def hotel_nights(request: ItineraryPlanRequest) -> int:
    return max(request.resolved_trip_days - 1, 0)


def to_candidate(listing: Listing, budget_level: BudgetLevel) -> Candidate:
    business_type_name = (
        listing.business_type_rel.name if listing.business_type_rel else "unknown"
    ).lower()
    location = extract_lat_lng(listing.location)
    return Candidate(
        listing=listing,
        location=Location(**location) if location is not None else None,
        business_type_name=business_type_name,
        estimated_cost=estimate_cost(listing, business_type_name, budget_level),
        estimated_duration_hours=estimate_duration_hours(listing, business_type_name),
        interest_names={
            (interest.name or "").strip().lower()
            for interest in (listing.interests or [])
            if (interest.name or "").strip()
        },
    )


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
    if cost <= 260:
        return 8
    return 14


def estimate_cost(
    listing: Listing,
    business_type_name: str,
    budget_level: BudgetLevel,
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


def resolved_end_date(request: ItineraryPlanRequest) -> date:
    if request.end_date is not None:
        return request.end_date
    return day_at(request.start_date, request.resolved_trip_days - 1)


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
