"""User entity + доменна валідація email/password.

Валідація навмисно дзеркалить legacy-правила (пермісивний regex,
8+letter+digit). Strict-режим — окремий цикл, див. PLAN.md секція 3.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from internal.account.domain.config import MIN_PASSWORD_LEN

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    """Дзеркалить legacy `_utils.is_valid_email` 1-в-1."""
    return bool(email and _EMAIL_RE.match(email))


def is_strong_password(pw: str) -> bool:
    """Дзеркалить legacy `_utils.is_strong_password` 1-в-1: ≥8 символів, ≥1 літера, ≥1 цифра."""
    if not pw or len(pw) < MIN_PASSWORD_LEN:
        return False
    return any(c.isalpha() for c in pw) and any(c.isdigit() for c in pw)


@dataclass(frozen=True)
class User:
    id: str
    email: str
    password: str  # формат "<sha256_hex>:<salt_hex>" — legacy-сумісний
    status: str  # "pending" | "active"
    verify_token: str | None
    verify_token_issued_at: float

    def to_dict(self) -> dict:
        """Серіалізація у legacy dict-shape (для in-memory db-сумісності)."""
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password,
            "status": self.status,
            "verify_token": self.verify_token,
            "verify_token_issued_at": self.verify_token_issued_at,
        }
