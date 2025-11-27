"""remove widget position columns

Revision ID: 82e1cad9f41e
Revises: a618447426b6
Create Date: 2025-11-25 18:57:18.998466

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "82e1cad9f41e"
down_revision: Union[str, Sequence[str], None] = "a618447426b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop position columns (tables are empty, no data to migrate)."""
    op.drop_column("widgets", "position_x")
    op.drop_column("widgets", "position_y")
    op.drop_column("widgets", "size_w")
    op.drop_column("widgets", "size_h")


def downgrade() -> None:
    """Re-add columns with defaults."""
    op.add_column("widgets", sa.Column("position_x", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("widgets", sa.Column("position_y", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("widgets", sa.Column("size_w", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("widgets", sa.Column("size_h", sa.Integer(), nullable=False, server_default="1"))
