"""Auth feature — registration, login. Vertical slice service.

Sentinel errors map to ``AppError`` in handler.py.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import bcrypt

from app.features.auth.model import User
from app.features.auth.repository import Repository


def _hash_password(password: str) -> str:
    """Хешуємо bcrypt напряму, без passlib: той закинутий і тягне модуль
    crypt, якого в Python 3.13+ уже немає. Формат ($2b$) той самий."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


class InvalidCredentialsError(Exception):
    """auth.invalid_credentials"""


class Service:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    async def register(self, email: str, password: str) -> User:
        password_hash = _hash_password(password)
        u = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(UTC),
        )
        await self._repo.create(u)
        return u

    async def login(self, email: str, password: str) -> User:
        u = await self._repo.find_by_email(email)
        if u is None:
            raise InvalidCredentialsError()
        if not _verify_password(password, u.password_hash):
            raise InvalidCredentialsError()
        return u
