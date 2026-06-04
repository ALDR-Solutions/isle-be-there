from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.listings.models import Listing


class ListingInterest(SQLModel, table=True):
    __tablename__ = "listing_interests"

    listing_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("listings.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    interest_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("interests.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )


class InterestCategory(SQLModel, table=True):
    __tablename__ = "interest_categories"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    name: str = Field(sa_column=Column(Text, unique=True, nullable=False))
    description: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )

    interests: list["Interests"] = Relationship(back_populates="category_rel")


class Interests(SQLModel, table=True):
    __tablename__ = "interests"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    name: str = Field(sa_column=Column(String, unique=True, nullable=False))
    category_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("interest_categories.id", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )

    category_rel: Optional["InterestCategory"] = Relationship(
        back_populates="interests"
    )
    listings: list["Listing"] = Relationship(
        back_populates="interests",
        link_model=ListingInterest,
    )


class UserInterest(SQLModel, table=True):
    __tablename__ = "user_interests"

    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    interest_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("interests.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )


class BusinessTypeInterest(SQLModel, table=True):
    __tablename__ = "business_type_interests"

    business_type_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("business_types.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    interest_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("interests.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )