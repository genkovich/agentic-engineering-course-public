"""RegisterUseCase — оркестрація register flow.

Контракт мусить дзеркалити legacy `internal.users.registration.register` —
див. `tests/account/{contract,characterization}/`. Порядок перевірок
ОЧЕНЬ важливий (зафіксовано у 9 parametrize-кейсах):

    invalid_email  →  weak_password  →  rate_limited  →  email_taken
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass

from internal.account.domain.config import (
    RATE_LIMIT_MAX_PER_WINDOW,
    RATE_LIMIT_WINDOW_SECONDS,
)
from internal.account.domain.ports import (
    Clock,
    EmailSender,
    PasswordHasher,
    RateLimitStore,
    UsersRepo,
)
from internal.account.domain.user import User, is_strong_password, is_valid_email


@dataclass(frozen=True)
class RegisterUseCase:
    users: UsersRepo
    hasher: PasswordHasher
    rate_limit: RateLimitStore
    email: EmailSender
    clock: Clock

    def execute(self, email: str, password: str) -> dict:
        if not is_valid_email(email):
            return {"status": "error", "error": "invalid_email"}
        if not is_strong_password(password):
            return {"status": "error", "error": "weak_password"}

        now = self.clock.now()
        recent = self.rate_limit.list_recent(now, RATE_LIMIT_WINDOW_SECONDS)
        if len(recent) >= RATE_LIMIT_MAX_PER_WINDOW:
            return {"status": "error", "error": "rate_limited"}

        if self.users.find_by_email(email) is not None:
            return {"status": "error", "error": "email_taken"}

        user = User(
            id=secrets.token_hex(16),
            email=email,
            password=self.hasher.hash(password),
            status="pending",
            verify_token=secrets.token_hex(16),
            verify_token_issued_at=now,
        )
        self.users.insert(email, user.to_dict())
        self.email.send(email, f"Verify: {user.verify_token}")
        self.rate_limit.record(now)

        return {"status": "success", "user_id": user.id, "verify_token": user.verify_token}
