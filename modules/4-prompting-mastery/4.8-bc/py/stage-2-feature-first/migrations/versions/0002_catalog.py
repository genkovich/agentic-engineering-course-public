"""catalog — catalog_categories, catalog_products + seed.

Revision ID: 0002_catalog
Revises: 0001_auth
Create Date: 2026-05-03

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_catalog"
down_revision: Union[str, None] = "0001_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "catalog_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        "catalog_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("price_cents", sa.BigInteger(), nullable=False),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("catalog_categories.id"),
            nullable=False,
        ),
    )

    op.bulk_insert(
        sa.table(
            "catalog_categories",
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
            "catalog_products",
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
    op.drop_table("catalog_products")
    op.drop_table("catalog_categories")
