from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.notification import Notification


class NotificationRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, n: Notification) -> None:
        await self._session.execute(
            text(
                "INSERT INTO notifications (id, user_id, channel, payload, sent_at) "
                "VALUES (:id, :user_id, :channel, :payload, :sent_at)"
            ),
            {
                "id": n.id,
                "user_id": n.user_id,
                "channel": n.channel,
                "payload": n.payload,
                "sent_at": n.sent_at,
            },
        )
        await self._session.commit()
