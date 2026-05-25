"""Tests for availability validation logic (RED phase - tests fail before implementation)."""

from datetime import time

import pytest
from pydantic import ValidationError

from app.modules.availability.schemas import (
    ListingHoursBase,
    ListingHoursCreate,
    ServiceSlotsBase,
    ServiceSlotsCreate,
)


class TestListingHoursValidation:
    """Test ListingHours Pydantic schema validation."""

    def test_day_of_week_valid_range(self):
        """day_of_week 0-6 should be valid."""
        for day in range(7):
            schema = ListingHoursBase(day_of_week=day, open_time=time(9, 0), close_time=time(18, 0))
            assert schema.day_of_week == day

    def test_day_of_week_below_range(self):
        """day_of_week=-1 should fail."""
        with pytest.raises(ValidationError) as exc_info:
            ListingHoursBase(day_of_week=-1, open_time=time(9, 0), close_time=time(18, 0))
        assert "day_of_week" in str(exc_info.value)

    def test_day_of_week_above_range(self):
        """day_of_week=7 should fail."""
        with pytest.raises(ValidationError) as exc_info:
            ListingHoursBase(day_of_week=7, open_time=time(9, 0), close_time=time(18, 0))
        assert "day_of_week" in str(exc_info.value)

    def test_open_time_required(self):
        """open_time is required."""
        with pytest.raises(ValidationError) as exc_info:
            ListingHoursBase(day_of_week=1, close_time=time(18, 0))
        assert "open_time" in str(exc_info.value)

    def test_close_time_required(self):
        """close_time is required."""
        with pytest.raises(ValidationError) as exc_info:
            ListingHoursBase(day_of_week=1, open_time=time(9, 0))
        assert "close_time" in str(exc_info.value)

    def test_open_before_close_valid(self):
        """open_time < close_time should be valid."""
        schema = ListingHoursBase(
            day_of_week=1,
            open_time=time(9, 0),
            close_time=time(18, 0)
        )
        assert schema.open_time < schema.close_time

    def test_open_after_close_invalid(self):
        """open_time > close_time should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            ListingHoursBase(
                day_of_week=1,
                open_time=time(18, 0),
                close_time=time(9, 0)
            )
        # Pydantic validates that open_time < close_time via model_validator
        assert "open_time" in str(exc_info.value).lower() or "close_time" in str(exc_info.value).lower()

    def test_open_equal_close_invalid(self):
        """open_time == close_time should fail (0 duration)."""
        with pytest.raises(ValidationError):
            ListingHoursBase(
                day_of_week=1,
                open_time=time(9, 0),
                close_time=time(9, 0)
            )


class TestServiceSlotsValidation:
    """Test ServiceSlots Pydantic schema validation."""

    def test_day_of_week_valid_range(self):
        """day_of_week 0-6 should be valid."""
        for day in range(7):
            schema = ServiceSlotsBase(
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(11, 0),
                capacity=5
            )
            assert schema.day_of_week == day

    def test_day_of_week_out_of_range(self):
        """day_of_week outside 0-6 should fail."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceSlotsBase(day_of_week=10, start_time=time(9, 0), end_time=time(11, 0), capacity=5)
        assert "day_of_week" in str(exc_info.value)

    def test_start_time_required(self):
        """start_time is required."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceSlotsBase(day_of_week=1, end_time=time(11, 0), capacity=5)
        assert "start_time" in str(exc_info.value)

    def test_end_time_required(self):
        """end_time is required."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceSlotsBase(day_of_week=1, start_time=time(9, 0), capacity=5)
        assert "end_time" in str(exc_info.value)

    def test_start_before_end_valid(self):
        """start_time < end_time should be valid."""
        schema = ServiceSlotsBase(
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=5
        )
        assert schema.start_time < schema.end_time

    def test_start_after_end_invalid(self):
        """start_time > end_time should fail."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceSlotsBase(
                day_of_week=1,
                start_time=time(14, 0),
                end_time=time(11, 0),
                capacity=5
            )
        assert "start_time" in str(exc_info.value).lower() or "end_time" in str(exc_info.value).lower()

    def test_start_equal_end_invalid(self):
        """start_time == end_time should fail (0 duration)."""
        with pytest.raises(ValidationError):
            ServiceSlotsBase(
                day_of_week=1,
                start_time=time(9, 0),
                end_time=time(9, 0),
                capacity=5
            )

    def test_capacity_default(self):
        """capacity defaults to 1."""
        schema = ServiceSlotsBase(
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(11, 0)
        )
        assert schema.capacity == 1

    def test_capacity_minimum(self):
        """capacity must be >= 1."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceSlotsBase(
                day_of_week=1,
                start_time=time(9, 0),
                end_time=time(11, 0),
                capacity=0
            )
        assert "capacity" in str(exc_info.value)


class TestListingHoursUniqueness:
    """Test ListingHours uniqueness constraints (database-level)."""

    def test_listing_id_required_in_create(self):
        """ListingHoursCreate requires listing_id."""
        with pytest.raises(ValidationError) as exc_info:
            ListingHoursCreate(day_of_week=1, open_time=time(9, 0), close_time=time(18, 0))
        assert "listing_id" in str(exc_info.value)


class TestServiceSlotsUniqueness:
    """Test ServiceSlots uniqueness constraints (database-level)."""

    def test_service_id_required_in_create(self):
        """ServiceSlotsCreate requires service_id."""
        with pytest.raises(ValidationError) as exc_info:
            ServiceSlotsCreate(
                day_of_week=1,
                start_time=time(9, 0),
                end_time=time(11, 0),
                capacity=5
            )
        assert "service_id" in str(exc_info.value)