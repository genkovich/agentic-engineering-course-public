---
name: notifications-bc-rules
description: Rules для Notifications Bounded Context
paths:
  - "src/notifications/**"
---

# Notifications BC

Scope: відправка email / push / sms. Notifications — sink BC, тільки слухає інших.

## Структура

```
src/notifications/
├── domain/
│   ├── notification.ts    # Notification, Channel, Sender interface
│   ├── repository.ts      # Repository interface
│   └── events.ts          # (порожньо на цьому етапі — Notifications не публікує)
├── app/service.ts         # send use case
├── infra/
│   ├── postgres/notificationRepo.ts
│   ├── stub/sender.ts             # StubSender — лог у stdout (демо)
│   ├── events/subscriber.ts       # підписки на auth.UserRegistered, commerce.OrderPlaced, billing.SubscriptionCreated
│   └── http/handler.ts            # POST /notifications/test (manual trigger для дебагу/тестів)
└── module.ts
```

## Правила

- Domain не імпортує інших BC
- ❗ ВИНЯТОК: `src/notifications/infra/events/` має право імпортувати `<other-bc>/domain` для event subscription. Це задокументовано у `.dependency-cruiser.cjs` (rule `events-only-foreign-domain`). Інші piece of `src/notifications/infra/*` — ні
- Sender — interface у `domain/`. Конкретні реалізації у `infra/<provider>/` (поки тільки `stub/`)
- Production-варіант: `infra/email/` (SMTP), `infra/push/` (APNS/FCM), `infra/sms/` (Twilio etc)

## Cross-BC взаємодія

Notifications слухає:
- `auth.UserRegistered` → welcome email
- `commerce.OrderPlaced` → order confirmation email
- `billing.SubscriptionCreated` → welcome letter

Notifications не публікує event-ів на цьому етапі.

## Anti-patterns

- ❌ Reentry: `notifications` викликає `auth` чи `billing` напряму. Тільки слухає
- ❌ Бізнес-логіка типу «не шли email якщо у користувача статус X» — належить тому BC, який знає про статус. Notifications приймає event і шле — крапка
- ❌ Жорстке кодування шаблонів у `domain/`. Шаблони — конфіг або зберігаються в БД
- ❌ Імпорт `src/auth/app` чи `src/billing/app`. Тільки domain types для event subscription (через `infra/events/`)
