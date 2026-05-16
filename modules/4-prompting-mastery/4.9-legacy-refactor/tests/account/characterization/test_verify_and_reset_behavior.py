"""
Characterization tests — verify_email + reset_password as-is, з відомими
дефектами (empty-token match, timing leak, token overwrite).
"""
from __future__ import annotations

import pytest


# ===== verify_email ==========================================================


def test_verify_success_activates_user_and_clears_token(api, db_with_sentinel):
    reg = api["register"]("v@x.com", "Strong1A")
    api["verify_email"](reg["verify_token"])
    user = db_with_sentinel["v@x.com"]
    assert user["status"] == "active"
    assert user["verify_token"] is None


def test_verify_reused_token_is_invalid_after_first_success(api):
    reg = api["register"]("vr@x.com", "Strong1A")
    first = api["verify_email"](reg["verify_token"])
    second = api["verify_email"](reg["verify_token"])
    assert first == {"status": "success"}
    assert second == {"status": "error", "error": "token_invalid"}


@pytest.mark.parametrize("seconds_offset,expected_status,expected_error", [
    (0, "success", None),
    (599, "success", None),
    (600, "success", None),         # рівно на межі — ще валідний (`> 600`)
    (601, "error", "token_expired"),
    (3600, "error", "token_expired"),
])
def test_verify_ttl_boundary(api, frozen_time, seconds_offset, expected_status, expected_error):
    reg = api["register"]("ttl@x.com", "Strong1A")
    frozen_time(seconds_offset)
    result = api["verify_email"](reg["verify_token"])
    assert result["status"] == expected_status
    if expected_error:
        assert result["error"] == expected_error


def test_verify_unknown_token_returns_invalid(api):
    api["register"]("u@x.com", "Strong1A")
    result = api["verify_email"]("0" * 32)
    assert result == {"status": "error", "error": "token_invalid"}


def test_verify_empty_token_known_defect(account, frozen_time):
    """Known defect: '' матчить юзера з verify_token=='' — фіксуємо as-is."""
    db = {"_s": {}, "victim@x.com": {
        "verify_token": "",
        "verify_token_issued_at": frozen_time.now(),
        "status": "pending",
    }}
    result = account.verify_email("", db=db)
    assert result == {"status": "success"}
    assert db["victim@x.com"]["status"] == "active"


# ===== reset_password ========================================================


def test_reset_password_known_email_writes_reset_token(api, db_with_sentinel, email_outbox):
    api["register"]("r@x.com", "Strong1A")
    api["reset_password"]("r@x.com")
    user = db_with_sentinel["r@x.com"]
    assert "reset_token" in user
    assert "reset_token_issued_at" in user
    assert isinstance(user["reset_token"], str) and len(user["reset_token"]) == 32
    assert isinstance(user["reset_token_issued_at"], float)


def test_reset_password_known_email_sends_email(api, email_outbox):
    api["register"]("rs@x.com", "Strong1A")
    email_outbox.clear()  # ігноруємо verify-лист
    api["reset_password"]("rs@x.com")
    assert len(email_outbox) == 1
    assert email_outbox[0]["to"] == "rs@x.com"


def test_reset_password_unknown_email_does_not_send_email_known_defect(api, email_outbox):
    """Known defect: unknown email → success, але без send_email → timing leak."""
    result = api["reset_password"]("ghost@x.com")
    assert result == {"status": "success"}
    assert email_outbox == [], "send_email не викликається для unknown — timing-leak"


def test_reset_password_overwrites_token_silently_known_defect(api, db_with_sentinel):
    """Known defect: повторний reset перезаписує reset_token, попередній — мертвий."""
    api["register"]("o@x.com", "Strong1A")
    api["reset_password"]("o@x.com")
    first_token = db_with_sentinel["o@x.com"]["reset_token"]
    api["reset_password"]("o@x.com")
    second_token = db_with_sentinel["o@x.com"]["reset_token"]
    assert first_token != second_token
