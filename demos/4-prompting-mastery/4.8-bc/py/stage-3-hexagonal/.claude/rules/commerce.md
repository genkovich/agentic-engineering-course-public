---
name: commerce-bc-rules
description: Rules for the Commerce Bounded Context (Python)
paths:
  - "app/commerce/**"
---

# Commerce BC

Scope: orders (simplified — no cart entity at this stage).

## Structure

```
app/commerce/
├── domain/
│   ├── order.py            # Order dataclass, OrderPlaced event, InvalidOrderError
│   └── repository.py       # Repository Protocol
├── app/service.py          # Place use case
├── infra/
│   ├── postgres/order_repo.py
│   └── http/handler.py     # POST /orders
└── module.py
```

## Rules

- `Order.user_id: UUID` — bare UUID, no FK to `auth_users` (BC isolation)
- `total_cents: int`, never `float`
- Status: `pending` (default), `paid`, `shipped`, `cancelled` — strings,
  validated in the use case
- Event publishing: `Service.place` → `bus.publish(OrderPlaced(...))`

## Cross-BC interaction

Commerce publishes:
- `OrderPlaced { order_id, user_id, total_cents, at }` — Billing subscribes
  (creates an Invoice — out of scope for the demo, only Subscriptions for now);
  Notifications subscribes (order confirmation email)

Commerce does not consume other BCs' events at this stage.

## Anti-patterns

- ❌ Direct call to `billing.Create...` / `notifications.Send...` in `Service.place`. Only via event
- ❌ Storing the full `User` entity inside `Order`. Only `user_id`
