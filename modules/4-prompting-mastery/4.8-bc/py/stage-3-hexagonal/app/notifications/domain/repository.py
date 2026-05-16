"""Notifications domain — Repository port."""
from __future__ import annotations

from typing import Protocol

from app.notifications.domain.notification import Notification


class Repository(Protocol):
    async def save(self, n: Notification) -> None: ...
