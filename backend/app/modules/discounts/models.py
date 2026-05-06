from enum import Enum
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY
from sqlalchemy.orm import Mapped


class DiscountType(str, Enum):
    PACKAGE = "package"
    VIP = "vip"
    REPEAT_CUSTOMER = "repeat_customer"
    HOLIDAY = "holiday"
    MANUAL = "manual"


class Discount(SQLModel, table=True):
    __tablename__ = "discounts"

    id: UUID = Field(default_factory=uuid4, nullable=False, primary_key=True)

    name: str = Field(sa_column=Column(String, nullable=False))

    discount_type: DiscountType = Field(
        sa_column=Column(SqlEnum(DiscountType, name="discount_type"), nullable=False)
    )

    discount_percent: float = Field(sa_column=Column(Float, nullable=False))

    min_services: Optional[int] = Field(default=None, nullable=True)

    required_business_types: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(ARRAY(String), nullable=True),
    )

    min_total_cost: Optional[float] = Field(default=None, nullable=True)
    max_discount_amount: Optional[float] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)
    valid_from: datetime = Field(nullable=False)
    valid_to: Optional[datetime] = Field(default=None, nullable=True)
    max_uses: Optional[int] = Field(default=None, nullable=True)
    current_uses: int = Field(default=0, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
