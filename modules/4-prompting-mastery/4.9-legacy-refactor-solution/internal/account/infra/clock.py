"""LegacyBackedClock — `internal.users._utils.time.time()` для сумісності з frozen_time.

Cleanup замінить на чистий `time.time()`. Контракт у `domain/ports.Clock`.
"""
from __future__ import annotations

import internal.users._utils as _legacy_utils


class LegacyBackedClock:
    def now(self) -> float:
        return _legacy_utils.time.time()
