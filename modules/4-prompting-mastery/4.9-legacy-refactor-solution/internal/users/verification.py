"""
internal/users/verification.py — legacy верифікація email.

Антипатерни:
- TTL 10 хв захардкожено через `time.time() - 600`, без посилання на конфіг
- Друге місце де ця ж 600 живе — `_utils.TOKEN_TTL_SECONDS`. Розсинхрон легко
  пропустити, бо вони не повʼязані
"""
from __future__ import annotations

import time


def verify_email(token: str, db=None):
    """Перевіряє token + активує користувача."""
    db = db or {}
    for email, user in db.items():
        if user.get("verify_token") == token:
            issued = user.get("verify_token_issued_at", 0)
            # TTL 10 хвилин — захардкожено тут, не у _utils
            if time.time() - issued > 600:
                return {"status": "error", "error": "token_expired"}
            user["status"] = "active"
            user["verify_token"] = None
            return {"status": "success"}
    return {"status": "error", "error": "token_invalid"}
