"""Orders endpoint."""

_ORDERS = [{"id": i, "total": i * 10} for i in range(1, 31)]


def get_order(order_id):
    """Return a single order by id, or None."""
    for order in _ORDERS:
        if order["id"] == order_id:
            return order
    return None
