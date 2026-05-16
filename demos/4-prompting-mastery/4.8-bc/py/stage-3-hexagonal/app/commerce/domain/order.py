"""Commerce domain — Order entity + OrderPlaced event."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.shared.events import Event


@dataclass
class Order:
    id: UUID
    user_id: UUID
    total_cents: int
    status: str
    created_at: datetime


class InvalidOrderError(Exception):
    """commerce.invalid_order"""


@dataclass
class OrderPlaced(Event):
    """Domain event — Notifications and Billing subscribe to it."""

    order_id: UUID
    user_id: UUID
    total_cents: int
    at: datetime

    @classmethod
    def name(cls) -> str:
        return "commerce.OrderPlaced"
