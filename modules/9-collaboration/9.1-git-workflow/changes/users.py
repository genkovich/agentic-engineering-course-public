"""Users listing endpoint."""

from api import pagination

_USERS = [{"id": i, "email": "user%d@example.com" % i} for i in range(1, 51)]


def list_users(cursor=None):
    """Return a page of users, starting from cursor (None = first page)."""
    if cursor is None:
        items = list(_USERS)
    else:
        items = [u for u in _USERS if u["id"] > cursor]
    return items[: pagination.LIMIT]
