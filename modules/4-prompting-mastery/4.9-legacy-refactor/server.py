"""
server.py — entry point застосунку (DI-точка, без веб-сервера).

Тут DI підключає поточну реалізацію users-модуля. У Step 4 (cutover)
ця імпорт-стрілка переключається з `internal.users` на `internal.account`
одним рядком. Без feature-flag, без branch-toggle.
"""
from __future__ import annotations


def setup_app(db: dict | None = None):
    """Створює застосунок з поточною реалізацією account-модуля."""
    db = db if db is not None else {}

    from internal.users import setup as account_setup

    return {"account": account_setup(db), "db": db}


if __name__ == "__main__":
    app = setup_app()
    print("App ready. account handlers:", list(app["account"].keys()))
