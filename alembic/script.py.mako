"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade database schema.
    
    This migration applies forward schema changes. Always test migrations
    in a development environment before applying to production.
    """
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade database schema.
    
    This migration reverts schema changes. Use with caution in production.
    Ensure data backups exist before running downgrades.
    """
    ${downgrades if downgrades else "pass"}
