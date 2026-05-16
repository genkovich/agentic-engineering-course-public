---
name: billing-bc-rules
description: Path-specific rules для Billing Bounded Context
paths:
  - "billing/**"
---

# Billing Bounded Context

Scope: підписки, оплата, інвойси. Все, що пов'язано з грошима — тут.

## Domain

Сутності: `Subscription`, `Invoice`, `PaymentMethod`. Гроші зберігаємо в `int64 cents`, ніколи не у `float64`.

Domain не знає про:
- Платіжного провайдера (Stripe, Liqpay) — це `billing/infra/<provider>/`
- Notifications — публікуємо event, не викликаємо напряму
- Auth — `Subscription.user_id` це просто UUID, не імпорт `auth.User`

## Що Billing публікує (events)

- `SubscriptionCreated { SubscriptionID, UserID, Plan }` — Notifications підписується для welcome-letter
- `PaymentSuccess { InvoiceID, Amount, PaidAt }` — Commerce оновлює статус замовлення
- `PaymentFailed { InvoiceID, Reason }` — Notifications шле email

## Що Billing споживає

- `OrderPlaced { OrderID, UserID, Total }` з Commerce — створюємо Invoice

## Гроші — окрема культура

- Завжди `int64` cents. Multiply / divide через бібліотеку чи окремі helper-функції
- Currency — окреме поле в типу, не припускай USD по дефолту
- Розрахунки тестуються на edge cases: round-half-even, від'ємні значення (refund), нульові суми

## Anti-patterns у цьому BC

- ❌ `float64` для money
- ❌ Прямий виклик `notifications.Send(...)` у use case. Натомість — `events.Publish(PaymentSuccess{...})`
- ❌ `Subscription` зберігає `User` сутність повністю. Тримай тільки `user_id`
