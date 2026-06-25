"""Access-token issuance.

Base version: tokens carry an expiry, but there is no refresh — an expired
token is simply invalid. The feat/token-refresh branch adds the refresh path,
and that branch-vs-main diff is what the agent summarises into a PR description.
"""

import time

TTL_SECONDS = 3600


def now():
    """Current timestamp in seconds."""
    return int(time.time())


def issue(user_id):
    """Issue a fresh access token for the user, valid for one hour."""
    return {
        "user_id": user_id,
        "token": "tok-%s" % user_id,
        "expires_at": now() + TTL_SECONDS,
    }


def is_valid(token):
    """True while the token has not reached its expiry."""
    return token.get("expires_at", 0) > now()
