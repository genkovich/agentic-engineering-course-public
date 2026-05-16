"""Commerce feature — Place use case."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.features.commerce.model import Order
from app.features.commerce.repository import Repository


class Service:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    async def place(self, user_id: UUID, total_cents: int) -> Order:
        o = Order(
            id=uuid4(),
            user_id=user_id,
            total_cents=total_cents,
            status="pending",
            created_at=datetime.now(UTC),
        )
        await self._repo.create(o)
        return o
