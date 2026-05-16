from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.model.notification import Notification
from app.repository.notification import NotificationRepo

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, repo: NotificationRepo) -> None:
        self._repo = repo

    async def send_test(
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
        logger.info("[stub-sender] %s -> user=%s payload=%r", channel, user_id, payload)
        await self._repo.create(n)
        return n
