"""Postgres adapter for Catalog Repository."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.catalog.domain.product import Product


class ProductRepo:
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self._session_maker = session_maker

    async def list(self) -> list[Product]:
        async with self._session_maker() as session:
            rows = (
                await session.execute(
                    text(
                        "SELECT id, name, price_cents, category_id "
                        "FROM catalog_products ORDER BY name"
                    )
                )
            ).all()
        return [
            Product(
                id=r.id,
                name=r.name,
                price_cents=r.price_cents,
                category_id=r.category_id,
            )
            for r in rows
        ]
