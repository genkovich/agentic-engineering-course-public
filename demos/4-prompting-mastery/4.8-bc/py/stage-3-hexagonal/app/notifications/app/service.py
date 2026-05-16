"""Notifications use case — Send.

Called by the HTTP handler (POST /notifications/test) and by event
subscribers (welcome email on UserRegistered, etc).
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.notifications.domain.notification import (
    Channel,
    Notification,
    Sender,
)
from app.notifications.domain.repository import Repository


class Service:
    def __init__(self, repo: Repository, sender: Sender) -> None:
        self._repo = repo
        self._sender = sender

    async def send(
        self, user_id: UUID, channel: Channel, payload: str
    ) -> Notification:
        n = Notification(
            id=uuid4(),
            user_id=user_id,
            channel=channel,
            payload=payload,
            sent_at=None,
        )
        await self._sender.send(n)
        n.sent_at = datetime.now(UTC)
        await self._repo.save(n)
        return n
