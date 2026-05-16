"""LegacyBackedRateLimitStore — backing store = `internal.users.reset_password_sync.recent_signups`.

ТРАНЗИТИВНО: під час cutover повторно використовуємо legacy-global, щоб
тести через `_PATCH_PATHS["recent_signups"]` лишалися чинними і autouse-fixture
чистила один список. Cleanup замінить на приватний list.

Контракт у `domain/ports.RateLimitStore`.
"""
from __future__ import annotations

import internal.users.reset_password_sync as _legacy_cache


class LegacyBackedRateLimitStore:
    def list_recent(self, now: float, window_s: float) -> list[float]:
        return [t for t in _legacy_cache.recent_signups if now - t < window_s]

    def record(self, now: float) -> None:
        _legacy_cache.recent_signups.append(now)
