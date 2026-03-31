from sqlmodel import SQLModel, CheckConstraint, UniqueConstraint, Field, Column, UUID as PGUUID, Integer, Text, ForeignKey, DateTime, text, JSON
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, date

class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
        UniqueConstraint("listing_id", "user_id", name="unique_review_per_user_per_listing"),
    )


    id: int = Field(sa_column=Column(Integer, primary_key=True, nullable=False))
    listing_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True), ForeignKey("listings.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False))
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        )
    )
    rating: int = Field(sa_column=Column(Integer, nullable=False))
    comment: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    auto_labels: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON, nullable=True))
    detected_language: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
