"""Users listing endpoint."""

from api import pagination

_USERS = [{"id": i, "email": "user%d@example.com" % i} for i in range(1, 51)]


def list_users(cursor):
    """Return a page of users after the given cursor."""
    items = [u for u in _USERS if u["id"] > cursor]
    return items[: pagination.LIMIT]
