"""add order_items table

Revision ID: ef9e4c6466bb
Revises: 6b58da2e9af0
Create Date: 2026-04-19 20:02:25.443763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef9e4c6466bb'
down_revision: Union[str, Sequence[str], None] = '6b58da2e9af0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Float, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("order_items")
