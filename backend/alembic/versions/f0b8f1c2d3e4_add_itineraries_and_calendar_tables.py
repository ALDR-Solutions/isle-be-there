"""add itineraries and calendar tables

Revision ID: f0b8f1c2d3e4
Revises: c82f3079f515
Create Date: 2026-04-16 13:10:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "f0b8f1c2d3e4"
down_revision: Union[str, Sequence[str], None] = "c82f3079f515"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "itineraries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("budget_level", sa.Text(), nullable=False),
        sa.Column("pace", sa.Text(), nullable=False),
        sa.Column("total_budget", sa.Float(), nullable=True),
        sa.Column("strict_budget", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("city", sa.Text(), nullable=True),
        sa.Column("country", sa.Text(), nullable=True),
        sa.Column("interests", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("preferred_business_types", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("total_estimated_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_itineraries_user_id"), "itineraries", ["user_id"], unique=False)

    op.create_table(
        "itinerary_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("itinerary_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("linked_booking_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("item_type", sa.Text(), nullable=False, server_default=sa.text("'stop'")),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("day_date", sa.Date(), nullable=False),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("estimated_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("address_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("reason_tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["itinerary_id"], ["itineraries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["linked_booking_id"], ["bookings.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_itinerary_items_itinerary_id"), "itinerary_items", ["itinerary_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_itinerary_items_itinerary_id"), table_name="itinerary_items")
    op.drop_table("itinerary_items")
    op.drop_index(op.f("ix_itineraries_user_id"), table_name="itineraries")
    op.drop_table("itineraries")
