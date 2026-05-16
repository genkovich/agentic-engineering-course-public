"""InMemoryUsersRepo — wrapper над legacy in-memory dict.

Контракт у `domain/ports.UsersRepo`. Cleanup-цикл замінить на ORM-репозиторій.
"""
from __future__ import annotations


class InMemoryUsersRepo:
    def __init__(self, db: dict) -> None:
        self._db = db

    def find_by_email(self, email: str) -> dict | None:
        return self._db.get(email)

    def insert(self, email: str, user_data: dict) -> None:
        self._db[email] = user_data
