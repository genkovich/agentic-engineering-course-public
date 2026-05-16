"""init — single revision creates all 5 tables (BC not expressed in schema).

Revision ID: 0001_init
Revises:
Create Date: 2026-05-03

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("price_cents", sa.BigInteger(), nullable=False),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id"),
            nullable=False,
        ),
    )

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("total_cents", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("plan", sa.String(50), nullable=False),
        sa.Column("next_charge_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.bulk_insert(
        sa.table(
            "categories",
            sa.column("id", postgresql.UUID(as_uuid=True)),
            sa.column("name", sa.String),
        ),
        [
            {"id": "11111111-1111-1111-1111-111111111111", "name": "Books"},
            {"id": "22222222-2222-2222-2222-222222222222", "name": "Electronics"},
        ],
    )

    op.bulk_insert(
        sa.table(
            "products",
            sa.column("id", postgresql.UUID(as_uuid=True)),
            sa.column("name", sa.String),
            sa.column("price_cents", sa.BigInteger),
            sa.column("category_id", postgresql.UUID(as_uuid=True)),
        ),
        [
            {
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "name": "A Philosophy of Software Design",
                "price_cents": 4500,
                "category_id": "11111111-1111-1111-1111-111111111111",
            },
            {
                "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "name": "Domain-Driven Design",
                "price_cents": 6500,
                "category_id": "11111111-1111-1111-1111-111111111111",
            },
            {
                "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                "name": "Mechanical Keyboard",
                "price_cents": 18900,
                "category_id": "22222222-2222-2222-2222-222222222222",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("subscriptions")
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("users")
