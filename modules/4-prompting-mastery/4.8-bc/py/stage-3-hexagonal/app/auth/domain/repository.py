"""Auth domain — UserRepository port (Protocol).

Implementations live in ``app.auth.infra.postgres``. Domain doesn't know
about pgx/asyncpg.
"""
from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.auth.domain.user import User


class UserRepository(Protocol):
    async def create(self, u: User) -> None: ...
    async def find_by_email(self, email: str) -> User | None: ...
    async def find_by_id(self, user_id: UUID) -> User | None: ...
