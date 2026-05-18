from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, DateTime, ForeignKey, Identity, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        UniqueConstraint("listing_id", "user_id", name="unique_review_per_user_per_listing"),
    )

    id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True), primary_key=True, nullable=False))
    listing_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("listings.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    rating: int = Field(sa_column=Column(Integer, nullable=False))
    comment: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    detected_language: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    classification_labels: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    is_flagged: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("false")),
    )
    is_visible: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("true")),
    )
    flag_reason: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    classified_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class BusinessReply(SQLModel, table=True):
    __tablename__ = "business_replies"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    review_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("reviews.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=True,
        )
    )
    business_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("businesses.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=True,
        )
    )
    description: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
