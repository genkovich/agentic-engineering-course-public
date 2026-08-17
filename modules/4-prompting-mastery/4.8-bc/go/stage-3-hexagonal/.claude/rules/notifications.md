---
name: notifications-bc-rules
description: Rules для Notifications Bounded Context
paths:
  - "notifications/**"
---

# Notifications BC

Scope: відправка email / push / sms. Notifications — sink BC, тільки слухає інших.

## Структура

```
notifications/
├── domain/notification.go    # Notification, Channel, Sender interface, Repository interface
├── app/service.go            # Send use case
├── infra/
│   ├── postgres/repo.go      # NotificationRepo
│   ├── stub/sender.go        # StubSender — лог у stdout (демо)
│   ├── events/subscriber.go  # підписки на auth.UserRegistered, commerce.OrderPlaced, billing.SubscriptionCreated
│   └── http/handler.go       # POST /notifications/test (manual trigger для дебагу/тестів)
└── module.go
```

## Правила

- Domain не імпортує інших BC
- ❗ ВИНЯТОК: `notifications/infra/events/` має право імпортувати `<other-bc>/domain` для event subscription. Це задокументовано в `.go-arch-lint.yml`. Інші piece of `notifications/infra/*` — ні
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
- ❌ Імпорт `auth/app` чи `billing/app`. Тільки domain types для event subscription (через `infra/events/`)
