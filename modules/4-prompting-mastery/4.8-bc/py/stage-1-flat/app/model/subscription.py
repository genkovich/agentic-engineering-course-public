from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Subscription:
    id: UUID
    user_id: UUID
    plan: str
    next_charge_at: datetime
    created_at: datetime
