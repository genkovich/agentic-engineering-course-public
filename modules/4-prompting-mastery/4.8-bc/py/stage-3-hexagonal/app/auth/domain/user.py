"""Auth domain — entity + UserRegistered event.

Domain does not import HTTP, DB, or other BCs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.shared.events import Event


@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    created_at: datetime


@dataclass
class UserRegistered(Event):
    """Domain event published via the bus.

    Notifications BC subscribes to send the welcome email.
    """

    user_id: UUID
    email: str
    at: datetime

    @classmethod
    def name(cls) -> str:
        return "auth.UserRegistered"
