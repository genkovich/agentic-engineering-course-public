"""Event subscribers for Notifications BC.

This is the ONE place where we cross BC boundaries: Notifications listens
to ``auth.UserRegistered``, ``commerce.OrderPlaced``,
``billing.SubscriptionCreated``. The cross-BC ``domain`` imports are
allowed by ``importlinter.ini`` exactly here (and only here).
"""
from __future__ import annotations

import logging

from app.auth.domain.user import UserRegistered
from app.billing.domain.subscription import SubscriptionCreated
from app.commerce.domain.order import OrderPlaced
from app.notifications.app.service import Service
from app.notifications.domain.notification import Channel
from app.shared.events import Event, EventBus

logger = logging.getLogger(__name__)


def register(bus: EventBus, svc: Service) -> None:
    async def on_user_registered(e: Event) -> None:
        assert isinstance(e, UserRegistered)
        try:
            await svc.send(e.user_id, Channel.EMAIL, "Welcome to our service!")
        except Exception:  # noqa: BLE001
            logger.exception("[notifications.subscriber] welcome email failed")

    async def on_order_placed(e: Event) -> None:
        assert isinstance(e, OrderPlaced)
        try:
            await svc.send(e.user_id, Channel.EMAIL, "Your order has been placed.")
        except Exception:  # noqa: BLE001
            logger.exception("[notifications.subscriber] order placed failed")

    async def on_subscription_created(e: Event) -> None:
        assert isinstance(e, SubscriptionCreated)
        try:
            await svc.send(
                e.user_id, Channel.EMAIL, f"Subscription confirmed: {e.plan}"
            )
        except Exception:  # noqa: BLE001
            logger.exception(
                "[notifications.subscriber] subscription created failed"
            )

    bus.subscribe(UserRegistered.name(), on_user_registered)
    bus.subscribe(OrderPlaced.name(), on_order_placed)
    bus.subscribe(SubscriptionCreated.name(), on_subscription_created)
