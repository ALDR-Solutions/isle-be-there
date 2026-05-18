from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field, SQLModel


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        UniqueConstraint(
            "listing_id", "user_id", name="unique_review_per_user_per_listing"
        ),
    )

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), primary_key=True, nullable=False, default=None
        )
    )
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
    comment: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    classification_labels: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        )
    )
