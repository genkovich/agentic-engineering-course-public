---
name: commerce-bc-rules
description: Rules для Commerce Bounded Context
paths:
  - "commerce/**"
---

# Commerce BC

Scope: замовлення (спрощено — без cart entity на цьому етапі).

## Структура

```
commerce/
├── domain/order.go       # Order, OrderPlaced event, ErrInvalidOrder
├── app/service.go        # Place use case
├── infra/
│   ├── postgres/repo.go
│   └── http/handler.go   # POST /orders
└── module.go
```

## Правила

- `Order.user_id` — UUID, не імпорт `auth.User` (BC isolation)
- `total_cents int64`, ніколи не `float64`
- Status: `pending` (default), `paid`, `shipped`, `cancelled` — рядки, валідація у app
- Event publishing: `service.Place` → `bus.Publish(OrderPlaced{...})`

## Cross-BC взаємодія

Commerce публікує:
- `OrderPlaced { OrderID, UserID, TotalCents, At }` — Billing підписаний (створює Invoice), Notifications підписаний (order confirmation)

Commerce не споживає event-ів інших BC на цьому етапі.

## Anti-patterns

- ❌ Прямий виклик `billing.Create...` чи `notifications.Send...` у `service.Place`. Тільки через event
- ❌ Зберігання `User` сутності в `Order`. Тільки `user_id`
