"""billing — billing_subscriptions.

Revision ID: 0004_billing
Revises: 0003_commerce
Create Date: 2026-05-03

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_billing"
down_revision: Union[str, None] = "0003_commerce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "billing_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan", sa.String(50), nullable=False),
        sa.Column("next_charge_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "billing_subscriptions_user_idx", "billing_subscriptions", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "billing_subscriptions_user_idx", table_name="billing_subscriptions"
    )
    op.drop_table("billing_subscriptions")
