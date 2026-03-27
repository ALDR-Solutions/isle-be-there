from sqlmodel import Column, DateTime, Field, ForeignKey, text, SQLModel, UUID as PGUUID
from uuid import UUID
from datetime import datetime


class UserInterest(SQLModel, table=True):
    __tablename__ = "user_interests"

    user_id: str = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )

    interest_id: str = Field(
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