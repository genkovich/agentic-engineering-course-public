from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.product import Product


class ProductRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self) -> list[Product]:
        rows = (
            await self._session.execute(
                text(
                    "SELECT id, name, price_cents, category_id "
                    "FROM products ORDER BY name"
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
