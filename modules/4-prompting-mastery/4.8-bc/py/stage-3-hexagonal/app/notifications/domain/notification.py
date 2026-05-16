"""Notifications domain — Notification entity, Channel enum, Sender port."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class Channel(StrEnum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


@dataclass
class Notification:
    id: UUID
    user_id: UUID
    channel: Channel
    payload: str
    sent_at: datetime | None


class Sender(Protocol):
    """Port. Implementations live in ``infra/{stub,email,push,sms}/``."""

    async def send(self, n: Notification) -> None: ...
