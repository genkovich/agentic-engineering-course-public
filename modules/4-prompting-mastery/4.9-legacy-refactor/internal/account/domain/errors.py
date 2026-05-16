"""Sentinel errors для register use case. Mapping → API codes у ports/errors.py."""
from __future__ import annotations


class AccountError(Exception):
    """Корінь ієрархії — будь-яка domain-помилка account-модуля."""


class InvalidEmail(AccountError):
    """Email не пройшов валідацію формату."""


class WeakPassword(AccountError):
    """Пароль не задовольняє domain-правилам сили."""


class RateLimited(AccountError):
    """Перевищено rate-limit на signup у поточному вікні."""


class EmailTaken(AccountError):
    """Email вже зареєстрований."""


class TokenExpired(AccountError):
    """Verify-токен прострочено (TTL > TOKEN_TTL_SECONDS)."""


class TokenInvalid(AccountError):
    """Verify-токен не знайдено або вже використано."""
