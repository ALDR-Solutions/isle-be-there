"""drop latitude and longitude from businesses

Revision ID: 1e49b51b4cf5
Revises: a1b2c3d4e5f6
Create Date: 2026-06-06 13:11:05.968734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '1e49b51b4cf5'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE businesses
        ADD COLUMN IF NOT EXISTS location geography
        """
    )

    op.execute(
        """
        UPDATE businesses
        SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
        WHERE location IS NULL
            AND latitude IS NOT NULL
            AND longitude IS NOT NULL
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_businesses_location
        ON businesses USING gist (location)
        """
    )

    op.execute(
        """
        ALTER TABLE businesses
        DROP COLUMN IF EXISTS latitude
        """
    )

    op.execute(
        """
        ALTER TABLE businesses
        DROP COLUMN IF EXISTS longitude
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE businesses
        ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION
        """
    )

    op.execute(
        """
        ALTER TABLE businesses
        ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION
        """
    )

    op.execute(
        """
        UPDATE businesses
        SET latitude = ST_Y(location::geometry),
            longitude = ST_X(location::geometry)
        WHERE location IS NOT NULL
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS idx_businesses_location
        """
    )

    op.execute(
        """
        ALTER TABLE businesses
        DROP COLUMN IF EXISTS location
        """
    )
