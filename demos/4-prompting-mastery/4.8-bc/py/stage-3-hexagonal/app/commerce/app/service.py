"""Commerce use cases — Place order."""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.commerce.domain.order import InvalidOrderError, Order, OrderPlaced
from app.commerce.domain.repository import Repository
from app.shared.events import EventBus


class Service:
    def __init__(self, repo: Repository, bus: EventBus) -> None:
        self._repo = repo
        self._bus = bus

    async def place(self, user_id: UUID, total_cents: int) -> Order:
        if total_cents < 0:
            raise InvalidOrderError()
        o = Order(
            id=uuid4(),
            user_id=user_id,
            total_cents=total_cents,
            status="pending",
            created_at=datetime.now(UTC),
        )
        await self._repo.create(o)
        await self._bus.publish(
            OrderPlaced(
                order_id=o.id,
                user_id=o.user_id,
                total_cents=o.total_cents,
                at=o.created_at,
            )
        )
        return o
