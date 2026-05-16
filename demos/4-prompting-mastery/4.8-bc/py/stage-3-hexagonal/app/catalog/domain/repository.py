"""Catalog domain — Repository port."""
from __future__ import annotations

from typing import Protocol

from app.catalog.domain.product import Product


class Repository(Protocol):
    async def list(self) -> list[Product]: ...
