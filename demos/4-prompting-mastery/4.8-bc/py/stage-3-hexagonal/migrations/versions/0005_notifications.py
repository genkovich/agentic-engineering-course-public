"""notifications — notifications_messages.

Revision ID: 0005_notifications
Revises: 0004_billing
Create Date: 2026-05-03

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005_notifications"
down_revision: Union[str, None] = "0004_billing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index(
        "notifications_messages_user_idx", "notifications_messages", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "notifications_messages_user_idx", table_name="notifications_messages"
    )
    op.drop_table("notifications_messages")
