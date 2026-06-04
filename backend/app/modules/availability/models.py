from datetime import time
from uuid import UUID

from sqlalchemy import Column, ForeignKey, Integer, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, Relationship, SQLModel


class ListingHours(SQLModel, table=True):
    __tablename__ = "listing_hours"

    id: int = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, nullable=False),
    )
    listing_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("listings.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    day_of_week: int = Field(nullable=False, ge=0, le=6)
    open_time: time = Field(nullable=False)
    close_time: time = Field(nullable=False)

    __table_args__ = (
        UniqueConstraint("listing_id", "day_of_week", name="uq_listing_hours_listing_day"),
    )

    listing_rel: "Listing" = Relationship(back_populates="listing_hours")


class ServiceSlots(SQLModel, table=True):
    __tablename__ = "service_slots"

    id: int = Field(
        sa_column=Column(Integer, primary_key=True, autoincrement=True, nullable=False),
    )
    service_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("services.service_id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        ),
    )
    day_of_week: int = Field(nullable=False, ge=0, le=6)
    start_time: time = Field(nullable=False)
    end_time: time = Field(nullable=False)
    capacity: int = Field(default=1, nullable=False)

    __table_args__ = (
        UniqueConstraint("service_id", "day_of_week", "start_time", name="uq_service_slots_service_day_start"),
    )

    service_rel: "Service" = Relationship(back_populates="service_slots")