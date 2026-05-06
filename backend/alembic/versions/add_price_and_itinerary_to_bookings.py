"""Alembic migration: add price and itinerary reference columns to bookings."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_price_itinerary_to_bookings'
down_revision = 'c82f3079f515'
branch_labels = None
depends_on = None


def upgrade():
    # monetary/price related columns
    op.add_column('bookings', sa.Column('base_price', sa.Float(), nullable=True))
    op.add_column('bookings', sa.Column('service_fee_percent', sa.Float(), nullable=True))
    op.add_column('bookings', sa.Column('service_fee_amount', sa.Float(), nullable=True))

    # discount columns with default 0
    op.add_column('bookings', sa.Column('discount_percent', sa.Float(), nullable=True, server_default=sa.text('0')))
    op.add_column('bookings', sa.Column('discount_amount', sa.Float(), nullable=True, server_default=sa.text('0')))

    # display/final pricing
    op.add_column('bookings', sa.Column('display_price', sa.Float(), nullable=True))
    op.add_column('bookings', sa.Column('final_price', sa.Float(), nullable=True))

    # itinerary relations (nullable)
    op.add_column('bookings', sa.Column('itinerary_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('bookings', sa.Column('itinerary_item_id', postgresql.UUID(as_uuid=True), nullable=True))

    # foreign key constraints
    op.create_foreign_key('fk_bookings_itinerary', 'bookings', 'itineraries', ['itinerary_id'], ['id'])
    op.create_foreign_key('fk_bookings_itinerary_item', 'bookings', 'itinerary_items', ['itinerary_item_id'], ['id'])


def downgrade():
    # drop foreign keys
    op.drop_constraint('fk_bookings_itinerary_item', 'bookings', type_='foreignkey')
    op.drop_constraint('fk_bookings_itinerary', 'bookings', type_='foreignkey')

    # remove columns in reverse order of creation
    op.drop_column('bookings', 'itinerary_item_id')
    op.drop_column('bookings', 'itinerary_id')
    op.drop_column('bookings', 'final_price')
    op.drop_column('bookings', 'display_price')
    op.drop_column('bookings', 'discount_amount')
    op.drop_column('bookings', 'discount_percent')
    op.drop_column('bookings', 'service_fee_amount')
    op.drop_column('bookings', 'service_fee_percent')
    op.drop_column('bookings', 'base_price')
