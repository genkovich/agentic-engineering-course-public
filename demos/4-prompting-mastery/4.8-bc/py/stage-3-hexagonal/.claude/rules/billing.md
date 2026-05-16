---
name: billing-bc-rules
description: Rules for the Billing Bounded Context (Python)
paths:
  - "app/billing/**"
---

# Billing BC

Scope: subscriptions, payments. Money is a separate culture.

## Structure

```
app/billing/
├── domain/
│   ├── subscription.py     # Subscription dataclass, SubscriptionCreated event, InvalidPlanError
│   └── repository.py       # Repository Protocol
├── app/service.py          # Subscribe use case (plan whitelist lives here)
├── infra/
│   ├── postgres/subscription_repo.py
│   └── http/handler.py     # POST /subscriptions
└── module.py
```

## Rules

- `int` cents, never `float` for money
- Plans — fixed whitelist (`basic`, `pro`, `enterprise`) in `app/service.py`.
  Adding a plan is a business decision
- Event publishing: `Service.subscribe` → `bus.publish(SubscriptionCreated(...))`
- Production-ready integration plugs a payment provider into
  `app/billing/infra/<provider>/` (Stripe, Liqpay) — implementations of
  `Charge` / `Refund` Protocols

## Anti-patterns

- ❌ `float` for money
- ❌ Direct call to `notifications.Send(...)` from a use case. Use
  `bus.publish(SubscriptionCreated(...))`
- ❌ Storing the full `User` entity inside `Subscription`. Only `user_id`
- ❌ Hard-coded provider logic in `domain/`. Domain knows only abstract
  `Charge`/`Invoice` concepts; the provider lives in infra
