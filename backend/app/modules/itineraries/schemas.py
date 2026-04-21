from datetime import date, datetime
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


class ItineraryStatus(str, Enum):
    draft = "draft"
    saved = "saved"
    archived = "archived"


class ItineraryPlanRequest(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    trip_days: Optional[int] = Field(default=None, ge=1, le=14)

    country: Optional[str] = None
    interests: list[str] = Field(default_factory=list)

    budget_level: BudgetLevel = BudgetLevel.medium
    pace: PaceLevel = PaceLevel.balanced

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

        self.interests = _normalize_strings(self.interests)
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
    description: Optional[str] = None
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


class ItinerarySaveRequest(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    status: ItineraryStatus = ItineraryStatus.saved
    plan_request: ItineraryPlanRequest
    plan_response: Optional[ItineraryPlanResponse] = None


class ItineraryItemResponse(BaseModel):
    id: UUID
    itinerary_id: UUID
    listing_id: Optional[UUID] = None
    linked_booking_id: Optional[UUID] = None
    item_type: str
    title: str
    description: Optional[str] = None
    day_date: date
    start_at: datetime
    end_at: datetime
    sort_order: int
    estimated_cost: float
    address_snapshot: Optional[dict] = None
    reason_tags: list[str] = Field(default_factory=list)
    extra_metadata: Optional[dict] = None


class SavedItinerarySummaryResponse(BaseModel):
    id: UUID
    title: str
    status: ItineraryStatus
    start_date: date
    end_date: date
    total_estimated_cost: float
    item_count: int
    created_at: datetime


class SavedItineraryResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    status: ItineraryStatus
    start_date: date
    end_date: date
    budget_level: BudgetLevel
    pace: PaceLevel
    total_budget: Optional[float] = None
    strict_budget: bool
    city: Optional[str] = None
    country: Optional[str] = None
    interests: list[str] = Field(default_factory=list)
    preferred_business_types: list[str] = Field(default_factory=list)
    total_estimated_cost: float
    created_at: datetime
    updated_at: datetime
    items: list[ItineraryItemResponse] = Field(default_factory=list)


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

