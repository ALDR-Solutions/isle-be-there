"""Drop listings start_time and end_time columns

Revision ID: b2c3d4e5f6a1
Revises: ab63a98b1261
Create Date: 2026-06-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a1"
down_revision: Union[str, Sequence[str], None] = "ab63a98b1261"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop start_time and end_time columns from listings table."""
    op.drop_column("listings", "end_time")
    op.drop_column("listings", "start_time")


def downgrade() -> None:
    """Re-add start_time and end_time columns to listings table."""
    op.add_column("listings", sa.Column("start_time", sa.DateTime(timezone=True), nullable=True))
    op.add_column("listings", sa.Column("end_time", sa.DateTime(timezone=True), nullable=True))
