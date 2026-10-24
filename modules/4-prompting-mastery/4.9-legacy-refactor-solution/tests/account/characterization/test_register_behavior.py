"""
Characterization tests — фіксують поточну behavior `register` as-is, включно
з відомими дефектами (TTL/rate-limit/case-sensitive). Це fix point of
reference: міграція не сміє змінювати ці кейси без явного PLAN-рішення.
"""
from __future__ import annotations

import re

import pytest

HEX32_RE = re.compile(r"^[0-9a-f]{32}$")


# ---- 1. Happy path ----------------------------------------------------------


def test_register_writes_full_user_shape_in_db(api, db_with_sentinel):
    result = api["register"]("u1@x.com", "Strong1A")
    assert result["status"] == "success"
    user = db_with_sentinel["u1@x.com"]
    assert set(user.keys()) == {
        "id", "email", "password", "status",
        "verify_token", "verify_token_issued_at",
    }
    assert user["email"] == "u1@x.com"
    assert user["status"] == "pending"
    assert user["id"] == result["user_id"]
    assert user["verify_token"] == result["verify_token"]
    assert ":" in user["password"], "password = '<sha256>:<salt>' формат"
    assert isinstance(user["verify_token_issued_at"], float)


def test_register_sends_verify_email_with_token(api, email_outbox):
    result = api["register"]("u2@x.com", "Strong1A")
    assert len(email_outbox) == 1
    sent = email_outbox[0]
    assert sent["to"] == "u2@x.com"
    assert result["verify_token"] in sent["body"]


# ---- 2. Validation order: invalid_email перевіряється ПЕРШИМ ----------------


@pytest.mark.parametrize(
    "email,password,expected_error",
    [
        # invalid_email спрацьовує до weak_password
        ("not-email", "weak", "invalid_email"),
        ("not-email", "Strong1A", "invalid_email"),
        ("", "Strong1A", "invalid_email"),
        ("a @b.com", "Strong1A", "invalid_email"),
        # weak_password — коли email валідний
        ("a@b.com", "weak", "weak_password"),
        ("a@b.com", "abcdefgh", "weak_password"),  # без цифри
        ("a@b.com", "12345678", "weak_password"),  # без літери
        ("a@b.com", "a1", "weak_password"),  # закоротко
        ("a@b.com", "", "weak_password"),
    ],
)
def test_register_validation_order(api, email, password, expected_error):
    result = api["register"](email, password)
    assert result == {"status": "error", "error": expected_error}


# ---- 3. email_taken (case-sensitive — known defect) -------------------------


def test_register_email_taken_exact_match(api):
    api["register"]("dup@x.com", "Strong1A")
    again = api["register"]("dup@x.com", "DifferP1A")
    assert again == {"status": "error", "error": "email_taken"}


def test_register_email_case_sensitive_collision_miss_known_defect(api):
    """Known defect: "A@B.COM" не матчить "a@b.com" — фіксуємо as-is."""
    api["register"]("a@b.com", "Strong1A")
    upper = api["register"]("A@B.COM", "Strong1A")
    assert upper["status"] == "success", "поточна behavior — обидва успішні"


# ---- 4. Rate limit (5 / 60s) ------------------------------------------------


def test_register_rate_limit_triggers_on_sixth_within_60s(api, frozen_time):
    for i in range(5):
        r = api["register"](f"u{i}@x.com", "Strong1A")
        assert r["status"] == "success"
    sixth = api["register"]("u5@x.com", "Strong1A")
    assert sixth == {"status": "error", "error": "rate_limited"}


def test_register_rate_limit_window_resets_after_60s(api, frozen_time):
    for i in range(5):
        api["register"](f"u{i}@x.com", "Strong1A")
    frozen_time(61)
    after = api["register"]("u5@x.com", "Strong1A")
    assert after["status"] == "success"


def test_register_rate_limit_does_not_count_invalid_email(api, frozen_time):
    for _ in range(10):
        api["register"]("not-email", "Strong1A")
    valid = api["register"]("ok@x.com", "Strong1A")
    assert valid["status"] == "success", "невалідні не повинні їсти бюджет"


# ---- 5. Side-effects: db mutated, recent_signups updated --------------------


def test_register_appends_to_recent_signups(api, db_with_sentinel):
    import importlib
    from tests.account.conftest import _PATCH_PATHS
    rps = importlib.import_module(_PATCH_PATHS["recent_signups"])
    assert rps.recent_signups == []
    api["register"]("rs@x.com", "Strong1A")
    assert len(rps.recent_signups) == 1


def test_register_silent_state_loss_when_db_falsy_known_defect(account):
    """Known defect: empty dict — falsy → `db or {}` рекинд → caller's db не мутується."""
    db = {}
    result = account.register("loss@x.com", "Strong1A", db=db)
    assert result["status"] == "success"
    assert db == {}, "caller's empty dict лишається empty (silent loss)"
