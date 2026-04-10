from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class BudgetLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class PaceLevel(str, Enum):
    relaxed = "relaxed"
    balanced = "balanced"
    packed = "packed"


class ItineraryPlanRequest(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    trip_days: Optional[int] = Field(default=None, ge=1, le=14)

    city: Optional[str] = None
    country: Optional[str] = None
    interests: list[str] = Field(default_factory=list)
    preferred_business_types: list[str] = Field(default_factory=list)

    budget_level: BudgetLevel = BudgetLevel.medium
    total_budget: Optional[float] = Field(default=None, gt=0)
    strict_budget: bool = True

    pace: PaceLevel = PaceLevel.balanced
    max_listings_per_day: Optional[int] = Field(default=None, ge=1, le=8)
    day_start_hour: int = Field(default=9, ge=0, le=23)
    day_end_hour: int = Field(default=21, ge=1, le=24)

    max_travel_km_between_stops: float = Field(default=30, gt=0, le=250)

    must_include_listing_ids: list[UUID] = Field(default_factory=list)
    excluded_listing_ids: list[UUID] = Field(default_factory=list)
    limit_candidates: int = Field(default=200, ge=20, le=500)

    @model_validator(mode="after")
    def _validate_dates_and_hours(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")

        if self.end_date and self.trip_days is not None:
            expected_days = (self.end_date - self.start_date).days + 1
            if expected_days != self.trip_days:
                raise ValueError("trip_days does not match start_date/end_date range")

        if not self.end_date and self.trip_days is None:
            raise ValueError("Provide either end_date or trip_days")

        if self.day_end_hour <= self.day_start_hour:
            raise ValueError("day_end_hour must be later than day_start_hour")

        self.interests = _normalize_strings(self.interests)
        self.preferred_business_types = _normalize_strings(self.preferred_business_types)
        return self

    @property
    def resolved_trip_days(self) -> int:
        if self.trip_days is not None:
            return self.trip_days
        # Validated above.
        return (self.end_date - self.start_date).days + 1  # type: ignore[union-attr]


class ItineraryStop(BaseModel):
    listing_id: UUID
    title: str
    business_type_name: Optional[str] = None
    address: Optional[dict] = None
    estimated_cost: float
    estimated_duration_hours: float
    start_time: str
    end_time: str
    score: float
    reason_tags: list[str] = Field(default_factory=list)


class ItineraryDay(BaseModel):
    date: date
    total_estimated_cost: float
    total_duration_hours: float
    stops: list[ItineraryStop] = Field(default_factory=list)


class ItineraryPlanResponse(BaseModel):
    trip_days: int
    budget_level: BudgetLevel
    pace: PaceLevel
    total_estimated_cost: float
    target_total_budget: Optional[float] = None
    daily_target_budget: float
    days: list[ItineraryDay] = Field(default_factory=list)


def _normalize_strings(items: list[str]) -> list[str]:
    normalized: list[str] = []
    seen = set()
    for item in items:
        value = (item or "").strip().lower()
        if not value or value in seen:
            continue
        normalized.append(value)
        seen.add(value)
    return normalized

