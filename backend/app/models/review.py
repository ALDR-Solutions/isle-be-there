from sqlmodel import (
    SQLModel,
    CheckConstraint,
    UniqueConstraint,
    Field,
    Column,
    UUID as PGUUID,
    Integer,
    Text,
    ForeignKey,
    DateTime,
    text,
)
from typing import Optional
from uuid import UUID
from datetime import datetime


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
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
    comment: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        )
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    classification_labels: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    classified_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    detected_language: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    translated_comment: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    censored_comment: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )


class BusinessReply(SQLModel, table=True):
    __tablename__ = "business_replies"
    __table_args__ = (UniqueConstraint("review_id", name="unique_reply_per_review"),)

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
            DateTime(timezone=True), nullable=False, server_default=text("now()")
        )
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    business_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("businesses.id", onupdate="CASCADE", ondelete="RESTRICT"),
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
    review_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("reviews.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        )
    )
    description: str = Field(sa_column=Column(Text, nullable=False))
