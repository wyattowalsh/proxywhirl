"""rename_proxy_uuid_to_id

Revision ID: 43cb4a16de9d
Revises: 6c3ceb558fef
Create Date: 2026-01-06 21:34:25.068775+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43cb4a16de9d'
down_revision: Union[str, None] = '6c3ceb558fef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.

    Rename 'proxy_uuid' column to 'id' to match the Proxy model definition.
    The ProxyTable model uses 'id' but the migration incorrectly created 'proxy_uuid'.
    This fixes the column name mismatch between model and database schema.

    This migration applies forward schema changes. Always test migrations
    in a development environment before applying to production.
    """
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table("proxies", schema=None) as batch_op:
        batch_op.alter_column(
            "proxy_uuid",
            new_column_name="id",
            existing_type=sa.String(),
            existing_nullable=True,
        )


def downgrade() -> None:
    """Downgrade database schema.

    Revert 'id' column back to 'proxy_uuid'.

    This migration reverts schema changes. Use with caution in production.
    Ensure data backups exist before running downgrades.
    """
    # Use batch operations for SQLite compatibility
    with op.batch_alter_table("proxies", schema=None) as batch_op:
        batch_op.alter_column(
            "id",
            new_column_name="proxy_uuid",
            existing_type=sa.String(),
            existing_nullable=True,
        )
