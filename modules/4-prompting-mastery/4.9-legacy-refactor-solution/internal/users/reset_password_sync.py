"""
internal/users/reset_password_sync.py — legacy email helper з глобальним кешем.

ДВА антипатерни в одному файлі:

1. `recent_signups` — module-level список, який пишеться з registration.py
   для rate-limit. Прихований глобальний state, який не очевидний з імені.

2. `send_email()` — імітує синхронне відправлення (sleep 200ms у проді).
   У тестах часто мокають це з мовчазним fallback на None — і тести
   стають привидами.

Ім'я файлу `reset_password_sync` — теж хардкод і анахронізм. Колись тут
жив тільки sync-варіант reset password, потім сюди додали все інше.
"""
from __future__ import annotations

import time

# глобальний кеш — пастка для рефакторингу (не очевидно з імені)
recent_signups: list[float] = []


def send_email(to: str, body: str) -> None:
    """Синхронно «шле» лист. У тестах — мок, у проді — блокує запит на 200-400ms."""
    # У реалі тут SMTP-виклик. Тут — sleep, щоби тести з реальним env лагали.
    time.sleep(0.001)  # 1ms у демо, у проді 200-400ms
    # лог немає, повернення немає — мовчазний side-effect
