---
name: commerce-bc-rules
description: Rules для Commerce Bounded Context
paths:
  - "src/commerce/**"
---

# Commerce BC

Scope: замовлення (спрощено — без cart entity на цьому етапі).

## Структура

```
src/commerce/
├── domain/
│   ├── order.ts          # Order, OrderPlaced event
│   ├── repository.ts     # Repository interface
│   └── errors.ts         # InvalidOrderError
├── app/service.ts        # Place use case
├── infra/
│   ├── postgres/orderRepo.ts
│   └── http/handler.ts   # POST /orders
└── module.ts
```

## Правила

- `Order.userId` — string (UUID), не імпорт `auth.User` (BC isolation)
- `totalCents: number` (cents у int64-friendly диапазоні), ніколи не `float`
- Status: `pending` (default), `paid`, `shipped`, `cancelled` — рядки, валідація у app
- Event publishing: `Service.place` → `bus.publish(new OrderPlaced(...))`

## Cross-BC взаємодія

Commerce публікує:
- `OrderPlaced { orderId, userId, totalCents, at }` — Billing підписаний (створює Invoice — не реалізовано в демо), Notifications підписаний (order confirmation)

Commerce не споживає event-ів інших BC на цьому етапі.

## Anti-patterns

- ❌ Прямий виклик `billing.subscribe(...)` чи `notifications.send(...)` у `Service.place`. Тільки через event
- ❌ Зберігання `User` сутності в `Order`. Тільки `userId`
