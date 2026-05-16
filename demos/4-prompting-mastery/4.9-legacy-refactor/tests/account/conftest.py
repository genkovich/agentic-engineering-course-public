"""
Fix point of reference для циклу users → account.

Імпорти/патчі ідуть через ці фікстури, а не напряму. У Step 4 (cutover)
оновлюємо рівно константи `ACCOUNT_MODULE` і `_PATCH_PATHS` нижче — тести
не змінюються.
"""
from __future__ import annotations

import importlib
from typing import Callable
from unittest.mock import MagicMock

import pytest

# === SWAP POINTS — оновлюються ОДНИМ рядком на Step 4 ===
ACCOUNT_MODULE = "internal.users"  # → "internal.account" після cutover

# Шляхи для monkeypatch. Якщо нова архітектура переносить ці seam-и —
# оновлюємо цей dict, тестові файли лишаються нечіпані.
_PATCH_PATHS = {
    "send_email": "internal.users.reset_password_sync.send_email",
    "recent_signups": "internal.users.reset_password_sync",  # модуль з global cache
    "time_utils": "internal.users._utils.time",
    "time_verification": "internal.users.verification.time",
    "time_password": "internal.users.password.time",
}


@pytest.fixture
def account():
    """Модуль під тестом. Cutover змінює лише ACCOUNT_MODULE."""
    return importlib.import_module(ACCOUNT_MODULE)


@pytest.fixture(autouse=True)
def _clean_recent_signups():
    """Гарантує ізоляцію rate-limit-кешу між тестами (легасі-глобал)."""
    mod = importlib.import_module(_PATCH_PATHS["recent_signups"])
    mod.recent_signups.clear()
    yield
    mod.recent_signups.clear()


@pytest.fixture
def email_outbox(monkeypatch) -> list[dict]:
    """Замінює send_email на колектор. Повертає список перехоплених листів."""
    sent: list[dict] = []

    def fake_send(to: str, body: str) -> None:
        sent.append({"to": to, "body": body})

    monkeypatch.setattr(_PATCH_PATHS["send_email"], fake_send)
    return sent


@pytest.fixture
def email_mock(monkeypatch) -> MagicMock:
    """Альтернатива email_outbox: MagicMock з assert_called_with API."""
    mock = MagicMock(return_value=None)
    monkeypatch.setattr(_PATCH_PATHS["send_email"], mock)
    return mock


@pytest.fixture
def frozen_time(monkeypatch):
    """Заморожує time.time() у всіх legacy-сайтах. Повертає advance(seconds)."""
    state = {"now": 1_700_000_000.0}

    def now() -> float:
        return state["now"]

    for key in ("time_utils", "time_verification", "time_password"):
        monkeypatch.setattr(f"{_PATCH_PATHS[key]}.time", now)

    def advance(seconds: float) -> None:
        state["now"] += seconds

    advance.now = lambda: state["now"]  # type: ignore[attr-defined]
    return advance


@pytest.fixture
def db_with_sentinel() -> dict:
    """Truthy db (sentinel key), щоб уникнути legacy-trap `db = db or {}`."""
    return {"_sentinel": {}}


@pytest.fixture
def api(db_with_sentinel) -> dict[str, Callable]:
    """DI handlers через server.setup_app — резолвиться у поточний cutover-стан.

    Step 4.1 hybrid: register → internal.account, verify/reset → internal.users.
    Тести через цю фікстуру автоматично йдуть туди, куди вказує setup_app,
    тому per-usecase cutover не вимагає правки тестових файлів.
    """
    from server import setup_app
    return setup_app(db_with_sentinel)["account"]
