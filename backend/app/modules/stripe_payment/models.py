"""Models for stripe payment module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class PaymentEvent(SQLModel, table=True):
    """
    Payment event model for tracking Stripe payment and refund events.

    Valid event_type values:
        - payment_intent.created: Payment intent was created
        - payment_intent.confirmed: Payment was confirmed
        - payment_intent.payment_failed: Payment failed
        - refund.initiated: Refund was initiated (T6)
        - refund.completed: Refund was completed
    """

    __tablename__ = "payment_events"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    booking_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("bookings.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
    event_type: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    stripe_payment_intent_id: Optional[str] = Field(
        default=None,
        sa_column=Column(
            Text,
            ForeignKey("bookings.stripe_payment_intent_id", onupdate="CASCADE", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    amount_cents: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, nullable=True),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )
