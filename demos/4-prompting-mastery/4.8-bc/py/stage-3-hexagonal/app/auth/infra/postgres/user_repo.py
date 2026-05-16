"""Postgres adapter for ``UserRepository`` Protocol.

Domain has no idea about asyncpg / SQLAlchemy. This file is the only place
that bridges the gap.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.auth.domain.errors import EmailAlreadyExistsError, UserNotFoundError
from app.auth.domain.user import User


class UserRepo:
    def __init__(self, session_maker: async_sessionmaker) -> None:
        self._session_maker = session_maker

    async def create(self, u: User) -> None:
        async with self._session_maker() as session:
            try:
                await session.execute(
                    text(
                        "INSERT INTO auth_users "
                        "(id, email, password_hash, created_at) "
                        "VALUES (:id, :email, :password_hash, :created_at)"
                    ),
                    {
                        "id": u.id,
                        "email": u.email,
                        "password_hash": u.password_hash,
                        "created_at": u.created_at,
                    },
                )
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise EmailAlreadyExistsError() from exc

    async def find_by_email(self, email: str) -> User | None:
        async with self._session_maker() as session:
            row = (
                await session.execute(
                    text(
                        "SELECT id, email, password_hash, created_at "
                        "FROM auth_users WHERE email = :email"
                    ),
                    {"email": email},
                )
            ).first()
        if row is None:
            return None
        return User(
            id=row.id,
            email=row.email,
            password_hash=row.password_hash,
            created_at=row.created_at,
        )

    async def find_by_id(self, user_id: UUID) -> User | None:
        async with self._session_maker() as session:
            row = (
                await session.execute(
                    text(
                        "SELECT id, email, password_hash, created_at "
                        "FROM auth_users WHERE id = :id"
                    ),
                    {"id": user_id},
                )
            ).first()
        if row is None:
            raise UserNotFoundError()
        return User(
            id=row.id,
            email=row.email,
            password_hash=row.password_hash,
            created_at=row.created_at,
        )
