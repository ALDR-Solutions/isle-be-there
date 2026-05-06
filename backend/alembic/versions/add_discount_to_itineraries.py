"""Migration: add applied_discount_id and discount_amount to itineraries.

Adds two new columns to the existing itineraries table:
- applied_discount_id: UUID foreign key to discounts.id (nullable)
- discount_amount: Float (nullable)

Notes:
- The itineraries table already exists; this is an ALTER operation only.
- A foreign key constraint is created to reference discounts(id).
- Downgrade drops the foreign key and the two columns.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_discount_to_itineraries'
down_revision = 'c82f3079f515_updated_bookings_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new columns (nullable as per requirements)
    op.add_column('itineraries', sa.Column('applied_discount_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('itineraries', sa.Column('discount_amount', sa.Float(), nullable=True))

    # Create FK constraint to discounts(id)
    op.create_foreign_key(
        'fk_itineraries_applied_discount_id_discounts',
        'itineraries',
        'discounts',
        ['applied_discount_id'],
        ['id'],
    )


def downgrade():
    # Remove FK constraint first, then drop columns
    op.drop_constraint('fk_itineraries_applied_discount_id_discounts', 'itineraries', type_='foreignkey')
    op.drop_column('itineraries', 'discount_amount')
    op.drop_column('itineraries', 'applied_discount_id')
