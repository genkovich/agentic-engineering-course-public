---
name: billing-bc-rules
description: Rules для Billing Bounded Context
paths:
  - "src/billing/**"
---

# Billing BC

Scope: підписки, оплати. Гроші — окрема культура.

## Структура

```
src/billing/
├── domain/
│   ├── subscription.ts   # Subscription, SubscriptionCreated event
│   ├── repository.ts     # Repository interface
│   └── errors.ts         # InvalidPlanError
├── app/service.ts        # Subscribe use case
├── infra/
│   ├── postgres/subscriptionRepo.ts
│   └── http/handler.ts   # POST /subscriptions
└── module.ts
```

## Правила

- `number` cents, ніколи `float`
- Plans — фіксований whitelist (`basic`, `pro`, `enterprise`) у `app/service.ts`. Зміна plans — це бізнес-рішення
- Event publishing: `Service.subscribe` → `bus.publish(new SubscriptionCreated(...))`
- Production-варіант підключатиме платіжного провайдера у `src/billing/infra/<provider>/` (Stripe, Liqpay) — реалізації Charge/Refund interfaces

## Anti-patterns

- ❌ `float` для money
- ❌ Прямий виклик `notifications.send(...)` у use case. Натомість — `bus.publish(new SubscriptionCreated(...))`
- ❌ Збереження повної `User` сутності у `Subscription`. Тримай тільки `userId`
- ❌ Hard-coded provider logic у `domain/`. Domain знає тільки про абстрактні `Charge`/`Invoice` концепти, провайдер — у infra
