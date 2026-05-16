"""Postgres adapter for Commerce Repository."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.commerce.domain.order import Order


class OrderRepo:
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self._session_maker = session_maker

    async def create(self, o: Order) -> None:
        async with self._session_maker() as session:
            await session.execute(
                text(
                    "INSERT INTO commerce_orders "
                    "(id, user_id, total_cents, status, created_at) "
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
            await session.commit()
