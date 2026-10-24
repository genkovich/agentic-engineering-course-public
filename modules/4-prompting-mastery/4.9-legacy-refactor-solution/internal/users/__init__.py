"""
internal/users — legacy спагетті-модуль.

ПОПЕРЕДЖЕННЯ для рефакторингу:
- глобальний `cache.recent_signups` у reset_password_sync
- TTL 10 хв захардкожено у verification.py
- синхронна email.send() у password.reset_password

Не редагуй цей модуль напряму. Усе нове пиши у `internal/account/`.
"""

from internal.users.registration import register
from internal.users.verification import verify_email
from internal.users.password import reset_password

__all__ = ["register", "verify_email", "reset_password", "setup"]


def setup(db):
    """Entry point for DI: returns module handlers bound to db."""
    return {
        "register": lambda email, password: register(email, password, db=db),
        "verify_email": lambda token: verify_email(token, db=db),
        "reset_password": lambda email: reset_password(email, db=db),
    }
