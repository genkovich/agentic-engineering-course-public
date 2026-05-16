"""
Contract tests — публічна поверхня account-модуля. Чорна скринька: тільки
return shape + статус-коди, без перевірки внутрішнього стану.
"""
from __future__ import annotations

import re

HEX32_RE = re.compile(r"^[0-9a-f]{32}$")


def test_module_exposes_setup_and_three_handlers(account):
    assert callable(account.setup)
    handlers = account.setup({"_sentinel": {}})
    assert set(handlers.keys()) == {"register", "verify_email", "reset_password"}
    for name in ("register", "verify_email", "reset_password"):
        assert callable(handlers[name]), f"{name} має бути callable"


def test_module_reexports_public_callables(account):
    for name in ("register", "verify_email", "reset_password", "setup"):
        assert hasattr(account, name), f"account.{name} має бути експортованим"


def test_register_success_shape(api):
    result = api["register"]("a@b.com", "Strong1A")
    assert result["status"] == "success"
    assert HEX32_RE.match(result["user_id"]), "user_id має бути 32 hex"
    assert HEX32_RE.match(result["verify_token"]), "verify_token має бути 32 hex"
    assert set(result.keys()) == {"status", "user_id", "verify_token"}


def test_register_error_shape_invalid_email(api):
    result = api["register"]("not-email", "Strong1A")
    assert result == {"status": "error", "error": "invalid_email"}


def test_register_error_shape_weak_password(api):
    result = api["register"]("a@b.com", "weak")
    assert result == {"status": "error", "error": "weak_password"}


def test_register_error_shape_email_taken(api):
    api["register"]("a@b.com", "Strong1A")
    second = api["register"]("a@b.com", "AnotherP1")
    assert second == {"status": "error", "error": "email_taken"}


def test_verify_email_success_shape(api):
    reg = api["register"]("v@b.com", "Strong1A")
    result = api["verify_email"](reg["verify_token"])
    assert result == {"status": "success"}


def test_verify_email_invalid_token_shape(api):
    result = api["verify_email"]("0" * 32)
    assert result == {"status": "error", "error": "token_invalid"}


def test_verify_email_expired_shape(api, frozen_time):
    reg = api["register"]("e@b.com", "Strong1A")
    frozen_time(601)
    result = api["verify_email"](reg["verify_token"])
    assert result == {"status": "error", "error": "token_expired"}


def test_reset_password_always_success_known(api, email_outbox):
    api["register"]("r@b.com", "Strong1A")
    result = api["reset_password"]("r@b.com")
    assert result == {"status": "success"}


def test_reset_password_always_success_unknown(api, email_outbox):
    """User-enumeration захист: success для unknown email теж."""
    result = api["reset_password"]("ghost@b.com")
    assert result == {"status": "success"}


def test_register_error_codes_are_closed_set(api):
    """Жоден інший error-код, окрім чотирьох оголошених, не має зʼявлятися."""
    allowed = {"invalid_email", "weak_password", "rate_limited", "email_taken"}
    cases = [
        api["register"]("not-email", "Strong1A"),
        api["register"]("a@b.com", "weak"),
    ]
    for r in cases:
        assert r["status"] == "error"
        assert r["error"] in allowed
