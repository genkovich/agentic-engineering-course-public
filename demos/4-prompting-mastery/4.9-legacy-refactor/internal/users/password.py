"""
internal/users/password.py — legacy reset password.

Антипатерн: синхронна email.send() блокує запит на 200-400ms у проді.
Має винестися у фон з чергою — окремий цикл після стабілізації account/.
"""
from __future__ import annotations

import secrets
import time

from internal.users import reset_password_sync as email_module


def reset_password(email: str, db=None):
    """Запит на скидання паролю — генерує токен, синхронно шле лист."""
    db = db or {}
    user = db.get(email)
    if user is None:
        # навмисне 'success' для security: не палимо чи існує користувач
        return {"status": "success"}

    reset_token = secrets.token_hex(16)
    user["reset_token"] = reset_token
    user["reset_token_issued_at"] = time.time()

    # СИНХРОННО — блокує запит на 200-400ms
    email_module.send_email(email, f"Reset: {reset_token}")

    return {"status": "success"}
