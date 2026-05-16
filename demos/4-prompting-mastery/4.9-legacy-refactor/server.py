"""
server.py — entry point для FastAPI.

Тут DI підключає поточну реалізацію users-модуля. У Step 4 (cutover)
ця імпорт-стрілка переключається з `internal.users` на `internal.account`
одним рядком. Без feature-flag, без branch-toggle.
"""
from __future__ import annotations


def setup_app(db: dict | None = None):
    """Створює застосунок з реалізацією account-модуля.

    Hybrid-стан після Step 4.1 (register cutover):
      - register → internal.account (новий код)
      - verify_email, reset_password → internal.users (legacy)
    Наступні use-case-cutover-и замінюватимуть по одній лямбді нижче.
    """
    db = db if db is not None else {}

    from internal.account.ports.handler import setup_register
    from internal.users import setup as legacy_setup

    legacy = legacy_setup(db)
    account = {
        "register": setup_register(db),
        "verify_email": legacy["verify_email"],
        "reset_password": legacy["reset_password"],
    }
    return {"account": account, "db": db}


if __name__ == "__main__":
    app = setup_app()
    print("App ready. account handlers:", list(app["account"].keys()))
