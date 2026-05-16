"""Port-Protocols — контракти, від яких залежить app-шар.

Адаптери у `infra/` структурно реалізують ці протоколи (duck typing).
App залежить ВИКЛЮЧНО від цього файлу, не від конкретних адаптерів.
"""
from __future__ import annotations

from typing import Protocol


class UsersRepo(Protocol):
    def find_by_email(self, email: str) -> dict | None: ...
    def insert(self, email: str, user_data: dict) -> None: ...


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...


class RateLimitStore(Protocol):
    def list_recent(self, now: float, window_s: float) -> list[float]: ...
    def record(self, now: float) -> None: ...


class EmailSender(Protocol):
    def send(self, to: str, body: str) -> None: ...


class Clock(Protocol):
    def now(self) -> float: ...
