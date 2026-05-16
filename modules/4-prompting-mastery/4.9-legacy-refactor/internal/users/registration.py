"""
internal/users/registration.py — legacy реєстрація.

Спагетті: validate + insert + email + rate-limit лезуть у одну функцію.
Глобальний `cache.recent_signups` — для rate-limit, але без коментаря,
звідки воно і чому.
"""
from __future__ import annotations

import hashlib
import secrets

from internal.users import reset_password_sync as cache_module  # для recent_signups
from internal.users._utils import is_valid_email, is_strong_password, now_seconds


def _hash_password(pw: str) -> str:
    salt = secrets.token_hex(8)
    return hashlib.sha256((salt + pw).encode()).hexdigest() + ":" + salt


def register(email: str, password: str, db=None):
    """
    Реєстрація користувача.

    Повертає dict з полями {status, user_id} або {status, error}.
    Старий код, не міняти. Замість нього у Step 4 пишемо internal/account/.
    """
    # 1) валідація
    if not is_valid_email(email):
        return {"status": "error", "error": "invalid_email"}
    if not is_strong_password(password):
        return {"status": "error", "error": "weak_password"}

    # 2) rate-limit через глобальний кеш (без коментаря, чому це тут)
    recent = cache_module.recent_signups
    now = now_seconds()
    recent[:] = [t for t in recent if now - t < 60]   # лишаємо тільки за останню хвилину
    if len(recent) >= 5:
        return {"status": "error", "error": "rate_limited"}
    recent.append(now)

    # 3) перевірка email_taken
    db = db or {}
    if email in db:
        return {"status": "error", "error": "email_taken"}

    # 4) збереження
    user_id = secrets.token_hex(16)
    verify_token = secrets.token_hex(16)
    db[email] = {
        "id": user_id,
        "email": email,
        "password": _hash_password(password),
        "status": "pending",
        "verify_token": verify_token,
        "verify_token_issued_at": now,
    }

    # 5) email — синхронно через reset_password_sync.send (пастка)
    cache_module.send_email(email, f"Verify: {verify_token}")

    return {"status": "success", "user_id": user_id, "verify_token": verify_token}
