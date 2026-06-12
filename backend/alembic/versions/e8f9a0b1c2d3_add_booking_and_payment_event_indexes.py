"""Add booking and payment event indexes for booking workflows

Revision ID: e8f9a0b1c2d3
Revises: d6e7f8a9b0c1
Create Date: 2026-06-12 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "e8f9a0b1c2d3"
down_revision: Union[str, Sequence[str], None] = "d6e7f8a9b0c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_bookings_user_created_at",
        "bookings",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_bookings_service_status_time_range",
        "bookings",
        ["service_id", "status", "booking_from_time", "booking_to_time"],
        unique=False,
    )
    op.create_index(
        "ix_payment_events_booking_event_type_created_at",
        "payment_events",
        ["booking_id", "event_type", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_payment_events_booking_event_type_created_at",
        table_name="payment_events",
    )
    op.drop_index("ix_bookings_service_status_time_range", table_name="bookings")
    op.drop_index("ix_bookings_user_created_at", table_name="bookings")
