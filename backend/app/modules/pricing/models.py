from __future__ import annotations

from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from sqlmodel import SQLModel, Field, Relationship


class PlatformPricingConfig(SQLModel, table=True):
    __tablename__ = "pricing_configs"
    # Index to optimize lookups by active status and validity window
    __table_args__ = (
        Index("ix_pricing_configs_is_active_from_to", "is_active", "effective_from", "effective_to"),
    )

    # UUID primary key with server default generation
    id: UUID = Field(
        sa_column=Column(
            PG_UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
        )
    )

    # Nullable FK to BusinessType. NULL means global/all business types
    business_type_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PG_UUID(as_uuid=True), ForeignKey("business_types.id"), nullable=True
        ),
    )

    # Relationship back to BusinessType; name mirrors pattern in other modules
    business_type_rel: Optional["BusinessType"] = Relationship(back_populates="pricing_configs")

    # Pricing fields
    service_fee_percent: float = Field()
    is_active: bool = Field()
    effective_from: datetime = Field()
    effective_to: Optional[datetime] = Field(default=None)
