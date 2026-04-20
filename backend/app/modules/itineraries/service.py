from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from math import atan2, cos, radians, sin, sqrt
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy import desc
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .model import Itinerary, ItineraryItem
from app.modules.listings.models import Listing, Statuses

from .schemas import (
    BudgetLevel,
    ItineraryDay,
    ItineraryPlanRequest,
    ItineraryPlanResponse,
    ItinerarySaveRequest,
    ItineraryStatus,
    ItineraryStop,
    PaceLevel,
    SavedItineraryResponse,
    SavedItinerarySummaryResponse,
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


def list_saved_itineraries(db: Session, user_id: UUID) -> list[SavedItinerarySummaryResponse]:
    itineraries = db.exec(
        select(Itinerary)
        .where(Itinerary.user_id == user_id)
        .order_by(desc(Itinerary.created_at))
    ).all()

    if not itineraries:
        return []

    itinerary_ids = [itinerary.id for itinerary in itineraries]
    item_rows = db.exec(
        select(ItineraryItem)
        .where(ItineraryItem.itinerary.__table__.c.id.in_(itinerary_ids))
    ).all()

    item_counts: dict[UUID, int] = {itinerary_id: 0 for itinerary_id in itinerary_ids}
    for item in item_rows:
        item_counts[item.itinerary_id] = item_counts.get(item.itinerary_id, 0) + 1

    return [
        SavedItinerarySummaryResponse(
            id=itinerary.id,
            title=itinerary.title,
            status=ItineraryStatus(itinerary.status),
            start_date=itinerary.start_date,
            end_date=itinerary.end_date,
            total_estimated_cost=float(itinerary.total_estimated_cost or 0),
            item_count=item_counts.get(itinerary.id, 0),
            created_at=itinerary.created_at,
        )
        for itinerary in itineraries
    ]


def get_saved_itinerary(db: Session, user_id: UUID, itinerary_id: UUID) -> SavedItineraryResponse:
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
        .order_by(ItineraryItem.day_date, ItineraryItem.sort_order, ItineraryItem.start_at)
    ).all()

    return _serialize_saved_itinerary(itinerary, items)


def save_itinerary(
    db: Session,
    user_id: UUID,
    payload: ItinerarySaveRequest,
) -> SavedItineraryResponse:
    planned = payload.plan_response or plan_itinerary(db, payload.plan_request)
    if len(planned.days) != payload.plan_request.resolved_trip_days:
        raise HTTPException(status_code=400, detail="Saved itinerary does not match requested trip length")

    itinerary = Itinerary(
        user_id=user_id,
        title=_resolved_title(payload),
        start_date=payload.plan_request.start_date,
        end_date=_resolved_end_date(payload.plan_request),
        status=payload.status.value,
        budget_level=payload.plan_request.budget_level.value,
        pace=payload.plan_request.pace.value,
        total_budget=payload.plan_request.total_budget,
        strict_budget=payload.plan_request.strict_budget,
        city=payload.plan_request.city,
        country=payload.plan_request.country,
        interests=payload.plan_request.interests,
        preferred_business_types=payload.plan_request.preferred_business_types,
        total_estimated_cost=float(planned.total_estimated_cost),
    )
    db.add(itinerary)
    db.flush()

    items = _build_items_for_saved_itinerary(itinerary.id, planned)
    for item in items:
        db.add(item)

    db.commit()
    db.refresh(itinerary)
    saved_items = db.exec(
        select(ItineraryItem)
        .where(ItineraryItem.itinerary_id == itinerary.id)
        .order_by(ItineraryItem.day_date, ItineraryItem.sort_order, ItineraryItem.start_at)
    ).all()

    return _serialize_saved_itinerary(itinerary, saved_items)


def delete_saved_itinerary(db: Session, user_id: UUID, itinerary_id: UUID) -> None:
    itinerary = db.exec(
        select(Itinerary)
        .where(Itinerary.id == itinerary_id)
        .where(Itinerary.user_id == user_id)
    ).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    db.delete(itinerary)
    db.commit()


def _load_candidates(db: Session, request: ItineraryPlanRequest) -> list[Candidate]:
    query = (
        select(Listing)
        .where(Listing.status == Statuses.active)
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


def _parse_hour_value(hour_value: str) -> time:
    try:
        hour_part, minute_part = hour_value.split(":", maxsplit=1)
        parsed_hour = int(hour_part)
        parsed_minute = int(minute_part)
    except (AttributeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid itinerary stop time format") from exc

    return time(hour=parsed_hour, minute=parsed_minute)


def _resolved_end_date(request: ItineraryPlanRequest) -> date:
    if request.end_date is not None:
        return request.end_date
    return _day_at(request.start_date, request.resolved_trip_days - 1)


def _resolved_title(payload: ItinerarySaveRequest) -> str:
    if payload.title and payload.title.strip():
        return payload.title.strip()

    location = payload.plan_request.city or payload.plan_request.country or "Trip"
    return f"{location} itinerary"


def _build_items_for_saved_itinerary(
    itinerary_id: UUID,
    planned: ItineraryPlanResponse,
) -> list[ItineraryItem]:
    items: list[ItineraryItem] = []

    for day_index, day in enumerate(planned.days):
        for stop_index, stop in enumerate(day.stops):
            start_at = datetime.combine(day.date, _parse_hour_value(stop.start_time))
            end_at = datetime.combine(day.date, _parse_hour_value(stop.end_time))
            items.append(
                ItineraryItem(
                    itinerary_id=itinerary_id,
                    listing_id=stop.listing_id,
                    item_type="stop",
                    title=stop.title,
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


def _serialize_saved_itinerary(
    itinerary: Itinerary,
    items: list[ItineraryItem],
) -> SavedItineraryResponse:
    return SavedItineraryResponse(
        id=itinerary.id,
        user_id=itinerary.user_id,
        title=itinerary.title,
        status=ItineraryStatus(itinerary.status),
        start_date=itinerary.start_date,
        end_date=itinerary.end_date,
        budget_level=BudgetLevel(itinerary.budget_level),
        pace=PaceLevel(itinerary.pace),
        total_budget=itinerary.total_budget,
        strict_budget=itinerary.strict_budget,
        city=itinerary.city,
        country=itinerary.country,
        interests=list(itinerary.interests or []),
        preferred_business_types=list(itinerary.preferred_business_types or []),
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

