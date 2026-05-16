from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Order:
    id: UUID
    user_id: UUID
    total_cents: int
    status: str
    created_at: datetime
