from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Notification:
    id: UUID
    user_id: UUID
    channel: str
    payload: str
    sent_at: datetime | None
