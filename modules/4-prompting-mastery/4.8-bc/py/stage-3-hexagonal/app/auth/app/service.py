"""Auth use cases — Register, Login.

Depends on the domain ``UserRepository`` Protocol and ``shared.events.EventBus``.
Knows nothing about HTTP or asyncpg.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import bcrypt

from app.auth.domain.errors import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.auth.domain.repository import UserRepository
from app.auth.domain.user import User, UserRegistered
from app.shared.events import EventBus


def _hash_password(password: str) -> str:
    """Хешуємо bcrypt напряму, без passlib: той закинутий і тягне модуль
    crypt, якого в Python 3.13+ уже немає. Формат ($2b$) той самий."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


class Service:
    def __init__(self, repo: UserRepository, bus: EventBus) -> None:
        self._repo = repo
        self._bus = bus

    async def register(self, email: str, password: str) -> User:
        password_hash = _hash_password(password)
        u = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(UTC),
        )
        try:
            await self._repo.create(u)
        except EmailAlreadyExistsError:
            raise
        await self._bus.publish(
            UserRegistered(user_id=u.id, email=u.email, at=u.created_at)
        )
        return u

    async def login(self, email: str, password: str) -> User:
        try:
            u = await self._repo.find_by_email(email)
        except UserNotFoundError as exc:
            raise InvalidCredentialsError() from exc
        if u is None:
            raise InvalidCredentialsError()
        if not _verify_password(password, u.password_hash):
            raise InvalidCredentialsError()
        return u
