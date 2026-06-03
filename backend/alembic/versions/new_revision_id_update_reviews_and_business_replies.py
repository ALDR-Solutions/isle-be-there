"""Update reviews and create business_replies table

Revision ID: new_revision_id
Revises: 8de4323faccf
Create Date: 2026-06-03 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "new_revision_id"
down_revision: Union[str, Sequence[str], None] = "8de4323faccf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop flag columns from reviews
    op.drop_column("reviews", "is_flagged")
    op.drop_column("reviews", "is_visible")
    op.drop_column("reviews", "flag_reason")

    # Convert reviews.id from Integer to UUID
    # First, drop identity constraint
    op.execute("ALTER TABLE reviews ALTER COLUMN id DROP IDENTITY IF EXISTS")

    # Add new UUID column with default (temporarily nullable)
    op.add_column(
        "reviews", sa.Column("id_new", postgresql.UUID(as_uuid=True), nullable=True)
    )

    # Generate UUIDs for existing rows
    op.execute("UPDATE reviews SET id_new = gen_random_uuid() WHERE id_new IS NULL")

    # Drop old integer id column
    op.drop_column("reviews", "id")

    # Rename new column to id
    op.alter_column("reviews", "id_new", new_column_name="id")

    # Make it non-nullable with PK constraint
    op.alter_column("reviews", "id", nullable=False)

    # Add new columns to reviews
    op.add_column("reviews", sa.Column("detected_language", sa.Text(), nullable=True))
    op.add_column("reviews", sa.Column("translated_comment", sa.Text(), nullable=True))
    op.add_column("reviews", sa.Column("censored_comment", sa.Text(), nullable=True))
    op.add_column(
        "reviews", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True)
    )

    # Create business_replies table
    op.create_table(
        "business_replies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "review_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reviews.id", onupdate="CASCADE", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("description", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop business_replies table
    op.drop_table("business_replies")

    # Remove new columns from reviews
    op.drop_column("reviews", "updated_at")
    op.drop_column("reviews", "censored_comment")
    op.drop_column("reviews", "translated_comment")
    op.drop_column("reviews", "detected_language")

    # Reverse UUID conversion (complex - note: existing UUID data will be lost)
    op.execute("ALTER TABLE reviews ALTER COLUMN id TYPE INTEGER")
    op.execute(
        "ALTER TABLE reviews ALTER COLUMN id SET DEFAULT nextval('reviews_id_seq'::regclass)"
    )
    op.execute("ALTER TABLE reviews ALTER COLUMN id DROP DEFAULT")

    # Note: is_flagged, is_visible, flag_reason cannot be restored by this downgrade
    # They would need a separate migration to restore
