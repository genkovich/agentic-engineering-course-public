"""apperr — typed errors used by every BC for cross-BC error semantics.

Each BC maps its own sentinel errors to ``AppError`` via its handler layer.
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
