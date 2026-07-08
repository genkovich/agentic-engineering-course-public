"""Tiny code surface: why the secret exists at all.

The payments client reads PAYMENTS_API_KEY from the environment. That is a normal,
legitimate reason for a secret to sit in .env next to the agent — which is exactly
why an over-permissioned agent that can read files AND reach the network is a
production exfiltration risk.
"""
import os


def charge(amount_cents: int) -> dict:
    key = os.environ.get("PAYMENTS_API_KEY", "")
    if not key:
        raise RuntimeError("PAYMENTS_API_KEY is not set")
    # (demo) a real client would call the payments provider here.
    return {"status": "ok", "amount_cents": amount_cents, "key_tail": key[-4:]}
