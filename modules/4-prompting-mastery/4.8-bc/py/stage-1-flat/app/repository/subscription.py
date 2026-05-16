from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.subscription import Subscription


class SubscriptionRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, s: Subscription) -> None:
        await self._session.execute(
            text(
                "INSERT INTO subscriptions "
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
        await self._session.commit()
