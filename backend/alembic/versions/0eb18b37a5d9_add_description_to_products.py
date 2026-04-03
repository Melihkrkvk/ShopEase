"""add description to products

Revision ID: 0eb18b37a5d9
Revises: 4e892772de03
Create Date: 2026-04-20 00:49:21.640940

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0eb18b37a5d9'
down_revision: Union[str, Sequence[str], None] = '4e892772de03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("products", sa.Column("description", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("products", "description")
