"""Async SQLAlchemy engine + session factory.

Cross-cutting infra utility — used by every repository.
"""
from __future__ import annotations

import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def _dsn() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://demo:demo@localhost:5432/demo",
    )


engine = create_async_engine(_dsn(), echo=False, future=True)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency — yields an AsyncSession for the request."""
    async with SessionMaker() as session:
        yield session
