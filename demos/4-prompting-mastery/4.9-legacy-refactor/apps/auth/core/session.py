"""
auth/core/session.py — Hard Rule: DO NOT modify.

Несуча стіна. Якщо тут зломити, ніхто не входить у систему.
Окремий цикл реалізації, окреме ревью. Не змішувати з legacy-рефакторингом.
"""
from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass


SESSION_TTL_SECONDS = 3600 * 24 * 7  # 7 днів — продакшн рішення, не міняти у legacy циклі


@dataclass(frozen=True)
class Session:
    user_id: str
    token: str
    issued_at: float

    def is_valid(self) -> bool:
        return time.time() - self.issued_at < SESSION_TTL_SECONDS


def issue_session(user_id: str) -> Session:
    raw = secrets.token_bytes(32)
    token = hashlib.sha256(raw).hexdigest()
    return Session(user_id=user_id, token=token, issued_at=time.time())
