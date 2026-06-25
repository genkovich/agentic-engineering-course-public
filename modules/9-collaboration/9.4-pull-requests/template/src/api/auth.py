"""Authentication: log a user in and hand back an access token."""

from api import token


def login(user_id):
    """Authenticate the user and issue an access token."""
    return token.issue(user_id)


def authorize(tok):
    """Allow the request only while the token is still valid.

    Base behaviour: an expired token is rejected and the caller has to log in
    again. The feat/token-refresh branch teaches this to refresh instead.
    """
    return token.is_valid(tok)
