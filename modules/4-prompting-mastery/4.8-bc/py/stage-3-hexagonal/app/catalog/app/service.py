"""Catalog use cases — List products."""
from __future__ import annotations

from app.catalog.domain.product import Product
from app.catalog.domain.repository import Repository


class Service:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    async def list(self) -> list[Product]:
        return await self._repo.list()
