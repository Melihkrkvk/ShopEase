"""add image_url to products

Revision ID: 4e892772de03
Revises: ef9e4c6466bb
Create Date: 2026-04-19 23:57:42.914290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e892772de03'
down_revision: Union[str, Sequence[str], None] = 'ef9e4c6466bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("products", sa.Column("image_url", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("products", "image_url")
