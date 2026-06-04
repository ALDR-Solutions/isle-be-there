"""Drop unique_review_per_user_per_listing constraint

Revision ID: a1b2c3d4e5f6
Revises: 75ecc05b3222
Create Date: 2026-06-04 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "75ecc05b3222"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("unique_review_per_user_per_listing"),
        "reviews",
        type_="unique",
    )


def downgrade() -> None:
    op.create_unique_constraint(
        "unique_review_per_user_per_listing",
        "reviews",
        ["listing_id", "user_id"],
    )
