"""Спільне для всіх скриптів демо 10.7.

Один клієнт Anthropic, читання/запис .env з id агента й оточення, і збірка
дифа review-target/ у текст рев'ю-запиту. Beta-header `managed-agents-2026-04-01`
SDK ставить сам - окремо його прописувати не треба.
"""

import os
from pathlib import Path

from anthropic import Anthropic

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
TARGET = ROOT / "review-target"

client = Anthropic()  # читає ANTHROPIC_API_KEY з оточення


def load_ids() -> dict[str, str]:
    """Повертає AGENT_ID / ENV_ID зі .env. Кидає, якщо setup.py ще не бігав."""
    ids: dict[str, str] = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            ids[key.strip()] = value.strip()
    missing = [k for k in ("AGENT_ID", "ENV_ID") if not ids.get(k)]
    if missing:
        raise SystemExit(
            f"У .env бракує {missing}. Спершу запусти: python setup.py"
        )
    return ids


def save_ids(agent_id: str, env_id: str) -> None:
    """Ідемпотентно пише id у .env (перезаписує наявні ключі)."""
    ENV_PATH.write_text(
        f"# згенеровано setup.py - id агента й оточення Managed Agents\n"
        f"AGENT_ID={agent_id}\n"
        f"ENV_ID={env_id}\n"
    )
    print(f"Записав id у {ENV_PATH}")


def review_request() -> str:
    """Складає рев'ю-запит: код review-target/ + що саме перевірити."""
    files = ["src/invoice.js", "src/discount.js", "src/money.js"]
    blocks = []
    for rel in files:
        code = (TARGET / rel).read_text()
        blocks.append(f"=== {rel} ===\n{code}")
    body = "\n\n".join(blocks)
    return (
        "Зроби код-рев'ю модуля рахунків нижче. Шукай помилки коректності, "
        "особливо в грошовій математиці. Для кожної знахідки дай файл, рядок, "
        "чому це баг і як полагодити. Тести в репозиторії зелені - не довіряй "
        "їм наосліп.\n\n"
        f"{body}"
    )
