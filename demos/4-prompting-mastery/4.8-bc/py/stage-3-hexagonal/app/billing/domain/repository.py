"""Billing domain — Subscription repository port."""
from __future__ import annotations

from typing import Protocol

from app.billing.domain.subscription import Subscription


class Repository(Protocol):
    async def create(self, s: Subscription) -> None: ...
