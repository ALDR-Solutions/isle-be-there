from uuid import UUID
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Column, DateTime, Text, text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .listing import Listing


class BusinessType(SQLModel, table=True):
    __tablename__ = "business_types"

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

    name: str = Field(sa_column=Column(Text, nullable=False, unique=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))

    listings: List["Listing"] = Relationship(back_populates="business_type_rel")
