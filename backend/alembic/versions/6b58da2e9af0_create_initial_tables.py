"""create initial tables

Revision ID: 6b58da2e9af0
Revises: 
Create Date: 2026-04-19 17:17:00.498028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b58da2e9af0'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("is_admin", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("stock", sa.Integer, nullable=False),
        sa.Column("category", sa.Text, nullable=False),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("payment_method", sa.Text, nullable=False),
        sa.Column("total", sa.Float, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default="pending"),
    )
    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("cart_id", sa.Integer, nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("cart_items")
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_table("users")
