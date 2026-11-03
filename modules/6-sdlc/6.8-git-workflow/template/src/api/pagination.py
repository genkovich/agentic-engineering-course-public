"""Cursor-based pagination for list endpoints."""

LIMIT = 20

# In-memory dataset standing in for a database table.
_ROWS = [{"id": i, "name": "item-%d" % i} for i in range(1, 101)]


def query_first():
    """First page of rows, used when no cursor is given."""
    return list(_ROWS)


def query(cursor):
    """Rows whose id is past the given cursor."""
    return [row for row in _ROWS if row["id"] > cursor]


def page(cursor=None):
    """Return one page of rows, starting from cursor."""
    items = query(cursor)
    return items[:LIMIT]
