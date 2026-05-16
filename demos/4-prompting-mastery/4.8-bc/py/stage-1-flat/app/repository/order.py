from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.order import Order


class OrderRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, o: Order) -> None:
        await self._session.execute(
            text(
                "INSERT INTO orders (id, user_id, total_cents, status, created_at) "
                "VALUES (:id, :user_id, :total_cents, :status, :created_at)"
            ),
            {
                "id": o.id,
                "user_id": o.user_id,
                "total_cents": o.total_cents,
                "status": o.status,
                "created_at": o.created_at,
            },
        )
        await self._session.commit()
