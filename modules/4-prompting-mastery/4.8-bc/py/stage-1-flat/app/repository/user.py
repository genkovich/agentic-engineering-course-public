from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.user import User


class UserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, u: User) -> None:
        await self._session.execute(
            text(
                "INSERT INTO users (id, email, password_hash, created_at) "
                "VALUES (:id, :email, :password_hash, :created_at)"
            ),
            {
                "id": u.id,
                "email": u.email,
                "password_hash": u.password_hash,
                "created_at": u.created_at,
            },
        )
        await self._session.commit()

    async def find_by_email(self, email: str) -> User | None:
        row = (
            await self._session.execute(
                text(
                    "SELECT id, email, password_hash, created_at "
                    "FROM users WHERE email = :email"
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
        row = (
            await self._session.execute(
                text(
                    "SELECT id, email, password_hash, created_at "
                    "FROM users WHERE id = :id"
                ),
                {"id": user_id},
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
