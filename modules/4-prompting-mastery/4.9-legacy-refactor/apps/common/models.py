"""
apps/common/models.py — Hard Rule: DO NOT modify (BaseModel).

BaseModel — предок ВСІХ моделей у проекті. Зміна одного поля = масовий
ALTER TABLE на всіх таблицях. Це окремий проектний цикл з міграційним
планом, не частина legacy-рефакторингу.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field


@dataclass
class BaseModel:
    """Спільний предок усіх моделей. Не змінювати поля без міграції на всі таблиці."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
