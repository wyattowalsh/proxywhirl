"""add_circuit_breaker_states

Revision ID: 6c3ceb558fef
Revises: a91638f44145
Create Date: 2026-01-06 21:34:09.215019+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c3ceb558fef'
down_revision: Union[str, None] = 'a91638f44145'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema.

    This migration applies forward schema changes. Always test migrations
    in a development environment before applying to production.
    """
    op.create_table(
        'circuit_breaker_states',
        sa.Column('proxy_id', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('failure_count', sa.Integer(), nullable=False),
        sa.Column('failure_window_json', sa.String(), nullable=False),
        sa.Column('next_test_time', sa.Float(), nullable=True),
        sa.Column('last_state_change', sa.DateTime(), nullable=False),
        sa.Column('failure_threshold', sa.Integer(), nullable=False),
        sa.Column('window_duration', sa.Float(), nullable=False),
        sa.Column('timeout_duration', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('proxy_id')
    )
    op.create_index(op.f('ix_circuit_breaker_states_state'), 'circuit_breaker_states', ['state'], unique=False)


def downgrade() -> None:
    """Downgrade database schema.

    This migration reverts schema changes. Use with caution in production.
    Ensure data backups exist before running downgrades.
    """
    op.drop_index(op.f('ix_circuit_breaker_states_state'), table_name='circuit_breaker_states')
    op.drop_table('circuit_breaker_states')
