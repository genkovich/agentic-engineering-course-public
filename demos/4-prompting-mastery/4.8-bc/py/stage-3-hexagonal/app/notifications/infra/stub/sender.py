"""Stub Sender — logs to stdout. Demo only.

Production-grade adapters live in ``infra/email/`` (SMTP), ``infra/push/``
(APNS/FCM), ``infra/sms/`` (Twilio etc).
"""
from __future__ import annotations

import logging

from app.notifications.domain.notification import Notification

logger = logging.getLogger(__name__)


class StubSender:
    async def send(self, n: Notification) -> None:
        logger.info(
            "[stub-sender] %s -> user=%s payload=%r",
            n.channel,
            n.user_id,
            n.payload,
        )
