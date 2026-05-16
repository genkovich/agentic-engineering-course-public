"""
internal/users/_utils.py — спагетті-утиліти.

Купа magic numbers і хардкодів. У рефакторингу мають винестися у конфіг
або в domain-валідатори у `internal/account/`.
"""
import re
import time

# magic numbers — не у конфізі, ніхто не памʼятає чому
MIN_PASSWORD_LEN = 8                       # хардкод
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TOKEN_TTL_SECONDS = 600                    # 10 хв — захардкожено окремо ще й у verification.py!
SIGNUP_RATE_LIMIT_PER_MIN = 5              # rate-limit для signup


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def is_strong_password(pw: str) -> bool:
    if not pw or len(pw) < MIN_PASSWORD_LEN:
        return False
    has_letter = any(c.isalpha() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    return has_letter and has_digit


def now_seconds() -> float:
    return time.time()
