"""Add service_slot_id to bookings

Revision ID: c4d5e6f7a8b9
Revises: b2c3d4e5f6a1
Create Date: 2026-06-11 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("service_slot_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_bookings_service_slot_id_service_slots",
        "bookings",
        "service_slots",
        ["service_slot_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_bookings_service_slot_id_service_slots", "bookings", type_="foreignkey")
    op.drop_column("bookings", "service_slot_id")
