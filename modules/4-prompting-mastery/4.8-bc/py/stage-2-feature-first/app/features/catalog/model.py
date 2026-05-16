from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class Product:
    id: UUID
    name: str
    price_cents: int
    category_id: UUID
