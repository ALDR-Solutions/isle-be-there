from uuid import UUID
from datetime import datetime
from typing import Optional, TYPE_CHECKING

# SQLAlchemy imports — all column-level stuff comes from here
from sqlalchemy import Column, Boolean, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID

# SQLModel imports — only model/field/relationship stuff
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .profile import Profile


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=text("gen_random_uuid()"),
        )
    )
    email: str = Field(sa_column=Column(Text, unique=True, nullable=False, index=True))
    hashed_password: str = Field(sa_column=Column(Text, nullable=False))
    username: Optional[str] = Field(default=None, sa_column=Column(Text, unique=True, nullable=True))
    first_name: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    last_name: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    is_business: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default=text("false"))
    )
    is_super_admin: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default=text("false"))
    )
    is_active: bool = Field(
        default=True, sa_column=Column(Boolean, nullable=False, server_default=text("true"))
    )

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    )
    updated_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    profile: Optional["Profile"] = Relationship(back_populates="user")
