from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from geoalchemy2 import Geography
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Numeric, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlmodel import Field, Relationship, SQLModel



class Statuses(str, Enum):
    active = "active"
    inactive = "inactive"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Listing(SQLModel, table=True):
    __tablename__ = "listings"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )
    business_id: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("businesses.id"),
            nullable=True,
        ),
    )
    business_rel: Optional["Business"] = Relationship(back_populates="listings")
    title: str = Field(sa_column=Column(Text, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    address: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    base_price: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric, nullable=True))
    business_type: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("business_types.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    business_type_rel: Optional["BusinessType"] = Relationship(back_populates="listings")
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), nullable=True),
    )
    image_urls: Optional[list[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text), nullable=True),
    )
    status: Optional[Statuses] = Field(
        default=Statuses.pending,
        sa_column=Column(
            SAEnum(Statuses, name="statuses", create_type=False),
            nullable=True,
        ),
    )
    phone_number: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    email_address: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    location: Optional[Any] = Field(
        default=None,
        sa_column=Column(Geography, nullable=True),
    )
    embedding: Optional[list[float]] = Field(
        default=None,
        sa_column=Column(Vector(), nullable=True),
    )
    details: Optional[dict] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    start_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    end_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))



class EmployeeListings(SQLModel, table=True):
    __tablename__ = "employee_listings"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    employee_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
    listing_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("listings.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
