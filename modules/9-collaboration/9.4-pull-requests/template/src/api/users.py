"""Users listing endpoint."""

_USERS = [{"id": i, "email": "user%d@example.com" % i} for i in range(1, 51)]

LIMIT = 20


def list_users(cursor=0):
    """Return a page of users whose id is past the given cursor."""
    items = [u for u in _USERS if u["id"] > cursor]
    return items[:LIMIT]
