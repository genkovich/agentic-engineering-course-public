from __future__ import annotations

from app.model.product import Product
from app.repository.product import ProductRepo


class ProductService:
    def __init__(self, repo: ProductRepo) -> None:
        self._repo = repo

    async def list(self) -> list[Product]:
        return await self._repo.list()
