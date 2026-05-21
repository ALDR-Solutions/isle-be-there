"""add_stripe_payment_fields

Revision ID: d4a5b6c7e8f9
Revises: a1b2c3d4e5f6
Create Date: 2026-05-21 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4a5b6c7e8f9'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Stripe payment fields to bookings and create payment_events table."""
    # Add stripe_payment_intent_id to bookings table
    op.add_column('bookings', sa.Column('stripe_payment_intent_id', sa.Text(), nullable=True))

    # Create payment_events table
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


def downgrade() -> None:
    """Remove Stripe payment fields."""
    op.drop_table('payment_events')
    op.drop_column('bookings', 'stripe_payment_intent_id')