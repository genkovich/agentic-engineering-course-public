---
name: billing-bc-rules
description: Rules для Billing Bounded Context
paths:
  - "billing/**"
---

# Billing BC

Scope: підписки, оплати. Гроші — окрема культура.

## Структура

```
billing/
├── domain/subscription.go  # Subscription, SubscriptionCreated event, ErrInvalidPlan
├── app/service.go          # Subscribe use case
├── infra/
│   ├── postgres/repo.go
│   └── http/handler.go     # POST /subscriptions
└── module.go
```

## Правила

- `int64 cents`, ніколи `float64`
- Plans — фіксований whitelist (`basic`, `pro`, `enterprise`) у `app/service.go`. Зміна plans — це бізнес-рішення
- Event publishing: `service.Subscribe` → `bus.Publish(SubscriptionCreated{...})`
- Production-варіант підключатиме платіжного провайдера у `billing/infra/<provider>/` (Stripe, Liqpay) — реалізації Charge/Refund interfaces

## Anti-patterns

- ❌ `float64` для money
- ❌ Прямий виклик `notifications.Send(...)` у use case. Натомість — `events.Publish(SubscriptionCreated{...})`
- ❌ Збереження повної `User` сутності у `Subscription`. Тримай тільки `user_id`
- ❌ Hard-coded provider logic у `domain/`. Domain знає тільки про абстрактні `Charge`/`Invoice` концепти, провайдер — у infra
