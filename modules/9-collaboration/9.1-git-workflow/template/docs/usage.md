# Usage

Tiny in-memory API used by the Lecture 9.1 screencasts.

- `api.pagination.page(cursor)` — one page of rows.
- `api.users.list_users(cursor)` — one page of users.
- `api.orders.get_order(id)` — a single order.
- `api.auth.refresh_token(user, token)` — refresh an expired token.

Run the tests:

    cd src && python3 -m unittest discover -s tests
