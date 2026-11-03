"""Orders endpoint."""

from api import pagination

_ORDERS = [{"id": i, "total": i * 10} for i in range(1, 31)]


def get_order(order_id):
    """Return a single order by id, or None."""
    for order in _ORDERS:
        if order["id"] == order_id:
            return order
    return None


def list_orders(cursor=None):
    """Return a page of orders, starting from cursor (None = first page)."""
    if cursor is None:
        items = list(_ORDERS)
    else:
        items = [o for o in _ORDERS if o["id"] > cursor]
    return items[: pagination.LIMIT]
