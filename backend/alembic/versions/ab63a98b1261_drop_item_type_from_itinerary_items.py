"""drop item_type from itinerary_items

Revision ID: ab63a98b1261
Revises: 1e49b51b4cf5
Create Date: 2026-06-06 14:52:45.438458

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ab63a98b1261'
down_revision: Union[str, Sequence[str], None] = '1e49b51b4cf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("itinerary_items", "item_type")

def downgrade() -> None:
    op.add_column("itinerary_items", sa.Column("item_type", sa.Text(), nullable=True))
