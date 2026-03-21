from sqlmodel import Column, Field, SQLModel, text, String, DateTime, UUID as PGUUID
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any



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
    category: str = Field(sa_column=Column(String, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=text("now()"),
        )
    )