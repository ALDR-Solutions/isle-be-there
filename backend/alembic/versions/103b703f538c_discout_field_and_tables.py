"""discout_field_and_tables

Revision ID: 103b703f538c
Revises: d48264722ede
Create Date: 2026-05-06 10:56:18.639451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '103b703f538c'
down_revision: Union[str, Sequence[str], None] = 'd48264722ede'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create discounts table
    op.create_table('discounts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('discount_type', sa.Enum('PACKAGE', 'VIP', 'REPEAT_CUSTOMER', 'HOLIDAY', 'MANUAL', name='discount_type'), nullable=False),
    sa.Column('discount_percent', sa.Float(), nullable=False),
    sa.Column('min_services', sa.Integer(), nullable=True),
    sa.Column('required_business_types', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('min_total_cost', sa.Float(), nullable=True),
    sa.Column('max_discount_amount', sa.Float(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('valid_from', sa.DateTime(), nullable=False),
    sa.Column('valid_to', sa.DateTime(), nullable=True),
    sa.Column('max_uses', sa.Integer(), nullable=True),
    sa.Column('current_uses', sa.Integer(), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    # Create pricing_configs table
    op.create_table('pricing_configs',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_type_id', sa.UUID(), nullable=True),
    sa.Column('service_fee_percent', sa.Float(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('effective_from', sa.DateTime(), nullable=False),
    sa.Column('effective_to', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['business_type_id'], ['business_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_pricing_configs_is_active_from_to', 'pricing_configs', ['is_active', 'effective_from', 'effective_to'], unique=False)

    # Add new columns to itineraries
    op.add_column('itineraries', sa.Column('applied_discount_id', sa.Integer(), nullable=True))
    op.add_column('itineraries', sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=True))

    # Add new columns to bookings
    op.add_column('bookings', sa.Column('base_price', sa.Numeric(), nullable=True))
    op.add_column('bookings', sa.Column('service_fee_percent', sa.Numeric(), nullable=True))
    op.add_column('bookings', sa.Column('service_fee_amount', sa.Numeric(), nullable=True))
    op.add_column('bookings', sa.Column('discount_percent', sa.Numeric(), nullable=True))
    op.add_column('bookings', sa.Column('discount_amount', sa.Numeric(), nullable=True))
    op.add_column('bookings', sa.Column('display_price', sa.Numeric(), nullable=True))
    op.add_column('bookings', sa.Column('final_price', sa.Numeric(), nullable=True))
    op.add_column('bookings', sa.Column('itinerary_id', sa.UUID(), nullable=True))
    op.add_column('bookings', sa.Column('itinerary_item_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'bookings', 'itinerary_items', ['itinerary_item_id'], ['id'], onupdate='CASCADE', ondelete='RESTRICT')
    op.create_foreign_key(None, 'bookings', 'itineraries', ['itinerary_id'], ['id'], onupdate='CASCADE', ondelete='RESTRICT')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'bookings', type_='foreignkey')
    op.drop_constraint(None, 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'itinerary_item_id')
    op.drop_column('bookings', 'itinerary_id')
    op.drop_column('bookings', 'final_price')
    op.drop_column('bookings', 'display_price')
    op.drop_column('bookings', 'discount_amount')
    op.drop_column('bookings', 'discount_percent')
    op.drop_column('bookings', 'service_fee_amount')
    op.drop_column('bookings', 'service_fee_percent')
    op.drop_column('bookings', 'base_price')

    op.drop_column('itineraries', 'discount_amount')
    op.drop_column('itineraries', 'applied_discount_id')

    op.drop_index('ix_pricing_configs_is_active_from_to', table_name='pricing_configs')
    op.drop_table('pricing_configs')
    op.drop_table('discounts')
