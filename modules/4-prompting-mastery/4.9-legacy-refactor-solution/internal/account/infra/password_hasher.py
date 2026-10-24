"""Sha256SaltHasher — дзеркалить legacy hash-формат `<sha256_hex>:<salt_hex>`.

Контракт у `domain/ports.PasswordHasher`. Bcrypt/argon2 — окремий security-цикл.
"""
from __future__ import annotations

import hashlib
import secrets


class Sha256SaltHasher:
    def hash(self, password: str) -> str:
        salt = secrets.token_hex(8)
        digest = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{digest}:{salt}"
