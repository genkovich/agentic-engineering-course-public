"""Alembic environment — sync engine for migrations."""
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Allow override via env (for `DATABASE_URL=...` in Makefile).
db_url = os.getenv("DATABASE_URL")
if db_url:
        # Alembic ходить у базу синхронно, застосунок — асинхронно.
    # Тому async-драйвер міняємо на psycopg 3 і НАЗИВАЄМО його явно:
    # голий postgresql:// змушує SQLAlchemy вгадувати драйвер, а вгадує
    # вона psycopg2, якого в залежностях немає —
    # ModuleNotFoundError: No module named 'psycopg2'.
    db_url = db_url.replace("+asyncpg", "+psycopg")
    for prefix in ("postgresql://", "postgres://"):
        if db_url.startswith(prefix):
            db_url = "postgresql+psycopg://" + db_url[len(prefix):]
            break
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
