"""Authentication helpers: token refresh."""

import logging
import time

log = logging.getLogger("auth")


def now():
    """Current timestamp in seconds."""
    return int(time.time())


def is_expired(token):
    """True if the token has passed its expiry."""
    return token.get("expires_at", 0) <= now()


def issue_new(user):
    """Issue a fresh token for the user, valid for one hour."""
    return {
        "user": user,
        "token": "tok-" + str(user),
        "expires_at": now() + 3600,
    }


def refresh_token(user, token):
    """Return a valid token, refreshing it if the old one expired."""
    if is_expired(token):
        token = issue_new(user)
        log.info("[auth] token refreshed")
    return token
