"""Postgres adapter for Billing Repository."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.billing.domain.subscription import Subscription


class SubscriptionRepo:
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self._session_maker = session_maker

    async def create(self, s: Subscription) -> None:
        async with self._session_maker() as session:
            await session.execute(
                text(
                    "INSERT INTO billing_subscriptions "
                    "(id, user_id, plan, next_charge_at, created_at) "
                    "VALUES (:id, :user_id, :plan, :next_charge_at, :created_at)"
                ),
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "plan": s.plan,
                    "next_charge_at": s.next_charge_at,
                    "created_at": s.created_at,
                },
            )
            await session.commit()
