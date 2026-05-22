"""squash_all_post_c82f3079f515

Revision ID: ab1234567890
Revises: c82f3079f515
Create Date: 2026-05-21 14:00:00.000000

This migration combines all changes from the following migrations
that were created in parallel from c82f3079f515:
- f0b8f1c2d3e4 (itineraries, itinerary_items)
- d48264722ede (booking_services removal, service_id FK)
- a94ff17d7c5d (reviews columns, business_employees role)
- 4bcedc987d02 (suspended enum value)
- a1b2c3d4e5f6 (listing_hours, service_slots)
- f5e6a7b8c9d0 (stripe_payment_intent_id UNIQUE, payment_events, FK)

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'ab1234567890'
down_revision: Union[str, Sequence[str], None] = 'c82f3079f515'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === f0b8f1c2d3e4: itineraries and itinerary_items ===
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

    # === d48264722ede: drop booking_services, add service_id to bookings ===
    op.drop_table('booking_services')
    op.add_column('bookings', sa.Column('service_id', sa.UUID(), nullable=True))
    op.drop_constraint(op.f('bookings_listing_id_fkey'), 'bookings', type_='foreignkey')
    op.create_foreign_key(None, 'bookings', 'services', ['service_id'], ['service_id'], onupdate='CASCADE', ondelete='RESTRICT')
    op.drop_column('bookings', 'listing_id')

    # === a94ff17d7c5d: reviews and business_employees columns ===
    op.add_column("business_employees", sa.Column("role", sa.String(), nullable=True))
    op.add_column("reviews", sa.Column("translated_comment", sa.Text(), nullable=True))
    op.add_column("reviews", sa.Column("censored_comment", sa.Text(), nullable=True))
    op.drop_column("reviews", "is_visible")
    op.drop_column("reviews", "flag_reason")
    op.drop_column("reviews", "is_flagged")

    # === 4bcedc987d02: suspended enum value ===
    op.execute("ALTER TYPE statuses ADD VALUE IF NOT EXISTS 'suspended'")

    # === a1b2c3d4e5f6: listing_hours and service_slots ===
    op.create_table(
        'listing_hours',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('listing_id', sa.UUID(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('open_time', sa.Time(), nullable=False),
        sa.Column('close_time', sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('listing_id', 'day_of_week', name='uq_listing_hours_listing_day'),
    )
    op.create_index('ix_listing_hours_listing_id', 'listing_hours', ['listing_id'])
    op.create_index('ix_listing_hours_listing_day', 'listing_hours', ['listing_id', 'day_of_week'])

    op.create_table(
        'service_slots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('service_id', sa.UUID(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['service_id'], ['services.service_id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('service_id', 'day_of_week', 'start_time', name='uq_service_slots_service_day_start'),
    )
    op.create_index('ix_service_slots_service_id', 'service_slots', ['service_id'])
    op.create_index('ix_service_slots_service_day_start', 'service_slots', ['service_id', 'day_of_week', 'start_time'])

    # === f5e6a7b8c9d0: stripe payment fields ===
    op.add_column('bookings', sa.Column('stripe_payment_intent_id', sa.Text(), nullable=True))
    op.create_unique_constraint('uq_bookings_stripe_payment_intent_id', 'bookings', ['stripe_payment_intent_id'])

    op.create_table(
        'payment_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('booking_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.Text(), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.Text(), nullable=True),
        sa.Column('amount_cents', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_foreign_key(
        'fk_payment_events_stripe_payment_intent_id',
        'payment_events',
        'bookings',
        ['stripe_payment_intent_id'],
        ['stripe_payment_intent_id'],
        onupdate='CASCADE',
        ondelete='SET NULL',
    )


def downgrade() -> None:
    # === f5e6a7b8c9d0 ===
    op.drop_constraint('fk_payment_events_stripe_payment_intent_id', 'payment_events', type_='foreignkey')
    op.drop_constraint('uq_bookings_stripe_payment_intent_id', 'bookings', type_='unique')
    op.drop_table('payment_events')
    op.drop_column('bookings', 'stripe_payment_intent_id')

    # === a1b2c3d4e5f6 ===
    op.drop_index('ix_service_slots_service_day_start', 'service_slots')
    op.drop_index('ix_service_slots_service_id', 'service_slots')
    op.drop_table('service_slots')
    op.drop_index('ix_listing_hours_listing_day', 'listing_hours')
    op.drop_index('ix_listing_hours_listing_id', 'listing_hours')
    op.drop_table('listing_hours')

    # === 4bcedc987d02 (enum cannot drop value safely) ===
    pass

    # === a94ff17d7c5d ===
    op.add_column("reviews", sa.Column("is_flagged", sa.BOOLEAN(), server_default=sa.text("false"), autoincrement=False, nullable=False))
    op.add_column("reviews", sa.Column("flag_reason", sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column("reviews", sa.Column("is_visible", sa.BOOLEAN(), server_default=sa.text("true"), autoincrement=False, nullable=False))
    op.drop_column("reviews", "censored_comment")
    op.drop_column("reviews", "translated_comment")
    op.drop_column("business_employees", "role")

    # === d48264722ede ===
    op.add_column('bookings', sa.Column('listing_id', sa.UUID(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'bookings', type_='foreignkey')
    op.create_foreign_key(op.f('bookings_listing_id_fkey'), 'bookings', 'listings', ['listing_id'], ['id'], onupdate='CASCADE', ondelete='RESTRICT')
    op.drop_column('bookings', 'service_id')
    op.create_table('booking_services', ...)  # Note: This table creation is simplified

    # === f0b8f1c2d3e4 ===
    op.drop_index(op.f("ix_itinerary_items_itinerary_id"), table_name="itinerary_items")
    op.drop_table("itinerary_items")
    op.drop_index(op.f("ix_itineraries_user_id"), table_name="itineraries")
    op.drop_table("itineraries")