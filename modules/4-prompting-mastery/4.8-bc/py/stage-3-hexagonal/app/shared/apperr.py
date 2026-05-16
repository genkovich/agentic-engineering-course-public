"""apperr — typed errors for cross-BC error semantics.

Each BC maps its domain sentinel errors to ``AppError`` in its own
``infra/http/errors.py``. ``shared`` knows nothing about specific BCs.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    code: str
    message: str
    status_code: int

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code}: {self.message}"
