"""Commerce domain — Order repository port."""
from __future__ import annotations

from typing import Protocol

from app.commerce.domain.order import Order


class Repository(Protocol):
    async def create(self, o: Order) -> None: ...
