"""Shared async Postgres engine + session factory.

Cross-cutting infra utility. Each BC module receives ``SessionMaker`` and
injects ``AsyncSession`` instances into its repositories.
"""
from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def _dsn() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://demo:demo@localhost:5432/demo",
    )


engine = create_async_engine(_dsn(), echo=False, future=True)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)
