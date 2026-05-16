"""Catalog feature — list products."""
from __future__ import annotations

from app.features.catalog.model import Product
from app.features.catalog.repository import Repository


class Service:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    async def list(self) -> list[Product]:
        return await self._repo.list()
