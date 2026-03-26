from sqlmodel import SQLModel, Field, Column, DateTime, UUID as PGUUID, text, ForeignKey
from uuid import UUID
from datetime import datetime

class Favourites(SQLModel, table=True):
    __tablename__ = "favourites"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )

    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    
    listing_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("listings.id", ondelete="CASCADE"),
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