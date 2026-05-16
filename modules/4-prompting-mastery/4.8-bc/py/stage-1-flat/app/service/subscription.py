from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.model.subscription import Subscription
from app.repository.subscription import SubscriptionRepo


class SubscriptionService:
    def __init__(self, repo: SubscriptionRepo) -> None:
        self._repo = repo

    async def subscribe(self, user_id: UUID, plan: str) -> Subscription:
        now = datetime.now(UTC)
        sub = Subscription(
            id=uuid4(),
            user_id=user_id,
            plan=plan,
            next_charge_at=now + timedelta(days=30),
            created_at=now,
        )
        await self._repo.create(sub)
        return sub
