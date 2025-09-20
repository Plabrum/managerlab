"""Initial migration

Revision ID: initial_migration
Revises:
Create Date: 2025-09-12 15:37:07.160688

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "initial_migration"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
