"""add_health_status_index

Revision ID: a91638f44145
Revises: a1b2c3d4e5f6
Create Date: 2026-01-06 21:33:50.334996+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a91638f44145'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.

    This migration applies forward schema changes. Always test migrations
    in a development environment before applying to production.
    """
    # Add index on health_status column for improved query performance
    op.create_index('ix_proxies_health_status', 'proxies', ['health_status'])


def downgrade() -> None:
    """Downgrade database schema.

    This migration reverts schema changes. Use with caution in production.
    Ensure data backups exist before running downgrades.
    """
    # Remove health_status index
    op.drop_index('ix_proxies_health_status', 'proxies')
