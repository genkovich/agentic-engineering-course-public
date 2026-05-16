"""Billing use cases — Subscribe.

The plan whitelist lives here, in the use case layer. Adding a plan is a
business decision that an admin / product manager owns.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.billing.domain.repository import Repository
from app.billing.domain.subscription import (
    InvalidPlanError,
    Subscription,
    SubscriptionCreated,
)
from app.shared.events import EventBus

VALID_PLANS = frozenset({"basic", "pro", "enterprise"})


class Service:
    def __init__(self, repo: Repository, bus: EventBus) -> None:
        self._repo = repo
        self._bus = bus

    async def subscribe(self, user_id: UUID, plan: str) -> Subscription:
        if plan not in VALID_PLANS:
            raise InvalidPlanError()
        now = datetime.now(UTC)
        sub = Subscription(
            id=uuid4(),
            user_id=user_id,
            plan=plan,
            next_charge_at=now + timedelta(days=30),
            created_at=now,
        )
        await self._repo.create(sub)
        await self._bus.publish(
            SubscriptionCreated(
                subscription_id=sub.id,
                user_id=sub.user_id,
                plan=sub.plan,
                at=sub.created_at,
            )
        )
        return sub
