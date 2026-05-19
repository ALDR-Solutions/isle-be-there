"""reviews_uuid_and_business_reply 

Revision ID: a94ff17d7c5d
Revises: f0b8f1c2d3e4
Create Date: 2026-05-08 13:42:40.840824

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a94ff17d7c5d"
down_revision: Union[str, Sequence[str], None] = "f0b8f1c2d3e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("business_employees", sa.Column("role", sa.String(), nullable=True))
    op.add_column("reviews", sa.Column("translated_comment", sa.Text(), nullable=True))
    op.add_column("reviews", sa.Column("censored_comment", sa.Text(), nullable=True))
    op.drop_column("reviews", "is_visible")
    op.drop_column("reviews", "flag_reason")
    op.drop_column("reviews", "is_flagged")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "reviews",
        sa.Column(
            "is_flagged",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "reviews",
        sa.Column("flag_reason", sa.TEXT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "reviews",
        sa.Column(
            "is_visible",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("reviews", "censored_comment")
    op.drop_column("reviews", "translated_comment")
    op.drop_column("business_employees", "role")
