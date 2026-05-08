"""add_suspended_listing_status

Revision ID: 4bcedc987d02
Revises: f0b8f1c2d3e4
Create Date: 2026-05-07 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4bcedc987d02"
down_revision: Union[str, Sequence[str], None] = "f0b8f1c2d3e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE statuses ADD VALUE IF NOT EXISTS 'suspended'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
