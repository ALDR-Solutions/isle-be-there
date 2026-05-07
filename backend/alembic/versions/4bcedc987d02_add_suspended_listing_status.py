"""add_suspended_listing_status

Revision ID: 4bcedc987d02
Revises: c82f3079f515
Create Date: 2026-05-07 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4bcedc987d02"
down_revision: Union[str, Sequence[str], None] = "c82f3079f515"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE statuses ADD VALUE IF NOT EXISTS 'suspended'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQL enums cannot drop a single value safely in place.
    pass
