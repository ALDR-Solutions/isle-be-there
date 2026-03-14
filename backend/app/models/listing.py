from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Text, text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel, Relationship
from geoalchemy2 import Geography
from pgvector.sqlalchemy import Vector

if TYPE_CHECKING:
    from .business import Business
    from .business_types import BusinessType

class Statuses(str, Enum):
    # Replace values with your actual enum labels from public.statuses
    active = "active"
    inactive = "inactive"
    pending = "pending"

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
    address: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB, nullable=True))
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

    image_urls: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(Text), nullable=True),
    )

    status: Optional[Statuses] = Field(
        default=None,
        sa_column=Column(
            SAEnum(Statuses, name="statuses", schema="public", create_type=False),
            nullable=True,
        ),
    )
    phone_number: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    email_address: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    location: Optional[Any] = Field(
        default=None,
        sa_column=Column(Geography, nullable=True),
    )

    # If you know the embedding dimension (e.g. 1536), use Vector(1536)
    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(Vector(), nullable=True),
    )
