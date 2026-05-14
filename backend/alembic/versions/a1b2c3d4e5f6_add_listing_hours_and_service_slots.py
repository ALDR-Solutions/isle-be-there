"""add_listing_hours_and_service_slots

Revision ID: a1b2c3d4e5f6
Revises: a94ff17d7c5d
Create Date: 2026-05-14 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'a94ff17d7c5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create listing_hours table
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

    # Create service_slots table
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


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_service_slots_service_day_start', 'service_slots')
    op.drop_index('ix_service_slots_service_id', 'service_slots')
    op.drop_table('service_slots')

    op.drop_index('ix_listing_hours_listing_day', 'listing_hours')
    op.drop_index('ix_listing_hours_listing_id', 'listing_hours')
    op.drop_table('listing_hours')