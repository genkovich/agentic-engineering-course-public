"""commerce — commerce_orders.

Revision ID: 0003_commerce
Revises: 0002_catalog
Create Date: 2026-05-03

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003_commerce"
down_revision: Union[str, None] = "0002_catalog"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # user_id — bare UUID, no FK to auth_users (BC isolation).
    op.create_table(
        "commerce_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_cents", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("commerce_orders_user_idx", "commerce_orders", ["user_id"])


def downgrade() -> None:
    op.drop_index("commerce_orders_user_idx", table_name="commerce_orders")
    op.drop_table("commerce_orders")
