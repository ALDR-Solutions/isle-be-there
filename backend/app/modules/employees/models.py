from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel, Field, Column, ForeignKey, text, String, DateTime, UUID as PGUUID

class Business_Employee(SQLModel, table=True):
    __tablename__ = "business_employees"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    business_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("businesses.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
    user_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
        )
    )
    role: str = Field(sa_column=Column(String, nullable=False))
    