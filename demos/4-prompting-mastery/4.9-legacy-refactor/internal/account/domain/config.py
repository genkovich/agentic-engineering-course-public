"""Single source of truth для domain-level констант."""
from __future__ import annotations

from typing import Final

MIN_PASSWORD_LEN: Final[int] = 8
TOKEN_TTL_SECONDS: Final[int] = 600
RATE_LIMIT_MAX_PER_WINDOW: Final[int] = 5
RATE_LIMIT_WINDOW_SECONDS: Final[int] = 60
