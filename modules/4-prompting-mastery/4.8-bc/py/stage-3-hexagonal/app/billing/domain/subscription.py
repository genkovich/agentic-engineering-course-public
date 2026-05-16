"""Billing domain — Subscription entity + SubscriptionCreated event."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.shared.events import Event


@dataclass
class Subscription:
    id: UUID
    user_id: UUID
    plan: str
    next_charge_at: datetime
    created_at: datetime


class InvalidPlanError(Exception):
    """billing.invalid_plan"""


@dataclass
class SubscriptionCreated(Event):
    """Domain event — Notifications subscribes for the welcome letter."""

    subscription_id: UUID
    user_id: UUID
    plan: str
    at: datetime

    @classmethod
    def name(cls) -> str:
        return "billing.SubscriptionCreated"
