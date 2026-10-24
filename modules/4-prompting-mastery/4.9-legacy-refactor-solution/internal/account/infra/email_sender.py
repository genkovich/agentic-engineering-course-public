"""LegacyBackedEmailSender — делегує до `internal.users.reset_password_sync.send_email`.

Late binding через атрибут-доступ — `email_outbox` фікстура (monkeypatch на
send_email) працює без змін. Cleanup замінить на власний async-адаптер.

Контракт у `domain/ports.EmailSender`.
"""
from __future__ import annotations

import internal.users.reset_password_sync as _legacy_email


class LegacyBackedEmailSender:
    def send(self, to: str, body: str) -> None:
        _legacy_email.send_email(to, body)
