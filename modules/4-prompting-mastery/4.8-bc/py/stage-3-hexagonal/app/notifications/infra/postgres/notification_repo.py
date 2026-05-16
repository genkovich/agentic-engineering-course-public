"""Postgres adapter for Notifications Repository."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.notifications.domain.notification import Notification


class NotificationRepo:
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self._session_maker = session_maker

    async def save(self, n: Notification) -> None:
        async with self._session_maker() as session:
            await session.execute(
                text(
                    "INSERT INTO notifications_messages "
                    "(id, user_id, channel, payload, sent_at) "
                    "VALUES (:id, :user_id, :channel, :payload, :sent_at)"
                ),
                {
                    "id": n.id,
                    "user_id": n.user_id,
                    "channel": str(n.channel),
                    "payload": n.payload,
                    "sent_at": n.sent_at,
                },
            )
            await session.commit()
