"""DI-handlers — будує RegisterUseCase з конкретними адаптерами.

`setup_register(db)` — точкова DI-точка для `register` під час hybrid-cutover.
Повертає callable `(email, password) -> dict`, який капсулює use case + db.
"""
from __future__ import annotations

from typing import Callable

from internal.account.app.register import RegisterUseCase
from internal.account.infra.clock import LegacyBackedClock
from internal.account.infra.email_sender import LegacyBackedEmailSender
from internal.account.infra.password_hasher import Sha256SaltHasher
from internal.account.infra.rate_limit import LegacyBackedRateLimitStore
from internal.account.infra.users_repo import InMemoryUsersRepo


def setup_register(db: dict | None = None) -> Callable[[str, str], dict]:
    """Будує register-handler. `db = db or {}` — навмисний legacy-trap parity."""
    db = db if db is not None else {}
    use_case = RegisterUseCase(
        users=InMemoryUsersRepo(db),
        hasher=Sha256SaltHasher(),
        rate_limit=LegacyBackedRateLimitStore(),
        email=LegacyBackedEmailSender(),
        clock=LegacyBackedClock(),
    )
    return lambda email, password: use_case.execute(email, password)
