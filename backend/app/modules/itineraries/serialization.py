from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from fastapi import HTTPException

from .models import Itinerary, ItineraryItem
from .schemas import (
    BudgetLevel,
    ItineraryDay,
    ItineraryPlanResponse,
    ItineraryStatus as ItinerarySchemaStatus,
    ItineraryStop,
    PaceLevel,
    SavedItineraryResponse,
)


def parse_hour_value(hour_value: str) -> time:
    try:
        hour_part, minute_part = hour_value.split(":", maxsplit=1)
        parsed_hour = int(hour_part)
        parsed_minute = int(minute_part)
    except (AttributeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid itinerary stop time format",
        ) from exc

    return time(hour=parsed_hour, minute=parsed_minute)


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


def serialize_saved_itinerary(
    itinerary: Itinerary,
    items: list[ItineraryItem],
    services_map: dict | None = None,
) -> SavedItineraryResponse:
    resolved_services_map = services_map or {}
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
                "service_id": (
                    resolved_services_map.get(item.listing_id)
                    if item.listing_id
                    else None
                ),
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
    daily_target_budget = round(total_estimated_cost / len(days), 2) if days else 0.0

    return ItineraryPlanResponse(
        trip_days=len(days),
        budget_level=saved_itinerary.budget_level,
        pace=saved_itinerary.pace,
        total_estimated_cost=round(total_estimated_cost, 2),
        target_total_budget=saved_itinerary.total_budget,
        daily_target_budget=daily_target_budget,
        days=days,
    )


def status_value(status) -> str:
    return status.value if hasattr(status, "value") else str(status)


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
