"""Notifications feature — Send use case (stub sender = log-to-stdout)."""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.features.notifications.model import Notification
from app.features.notifications.repository import Repository

logger = logging.getLogger(__name__)


class Service:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    async def send(
        self, user_id: UUID, channel: str, payload: str
    ) -> Notification:
        now = datetime.now(UTC)
        n = Notification(
            id=uuid4(),
            user_id=user_id,
            channel=channel,
            payload=payload,
            sent_at=now,
        )
        logger.info(
            "[stub-sender] %s -> user=%s payload=%r", channel, user_id, payload
        )
        await self._repo.save(n)
        return n
