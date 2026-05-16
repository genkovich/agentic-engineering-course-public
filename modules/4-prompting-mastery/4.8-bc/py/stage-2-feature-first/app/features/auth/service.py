"""Auth feature — registration, login. Vertical slice service.

Sentinel errors map to ``AppError`` in handler.py.
"""
from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from passlib.hash import bcrypt

from app.features.auth.model import User
from app.features.auth.repository import Repository


class InvalidCredentialsError(Exception):
    """auth.invalid_credentials"""


class Service:
    def __init__(self, repo: Repository) -> None:
        self._repo = repo

    async def register(self, email: str, password: str) -> User:
        password_hash = bcrypt.hash(password)
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
        if not bcrypt.verify(password, u.password_hash):
            raise InvalidCredentialsError()
        return u
