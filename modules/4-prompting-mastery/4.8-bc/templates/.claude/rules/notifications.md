---
name: notifications-bc-rules
description: Path-specific rules для Notifications Bounded Context
paths:
  - "notifications/**"
---

# Notifications Bounded Context

Scope: відправка email / push / sms. Всі канали комунікації з користувачем поза веб-інтерфейсом.

## Domain

Сутності: `Notification { id, user_id, channel, payload, sent_at }`, `Channel` enum (`email`, `push`, `sms`).

Інтерфейси у `notifications/domain/`:
- `Sender` — `Send(ctx, Notification) error`
- `Repository` — `Save(ctx, Notification) error`, `FindByUser(ctx, userID) ([]Notification, error)`

Конкретні реалізації — у `notifications/infra/<provider>/`:
- `notifications/infra/email/` — SMTP-адаптер
- `notifications/infra/push/` — APNS/FCM-адаптер
- `notifications/infra/sms/` — Twilio etc

## Що Notifications споживає (events)

Notifications — sink BC, тільки слухає:

- `auth.UserRegistered` → welcome email
- `commerce.OrderPlaced` → order confirmation email
- `billing.PaymentFailed` → payment failure notification
- `billing.SubscriptionCreated` → welcome letter

Підписники у `notifications/infra/events/subscriber.go` — реєструють handlers через registrar.

## Що Notifications публікує

Зазвичай нічого назовні. Якщо потрібен audit trail — `NotificationSent { ID, Channel, SentAt }` для analytics.

## Анти-патерни у цьому BC

- ❌ Reentry. `Notifications` не викликає `auth` чи `billing` напряму. Тільки слухає їх події
- ❌ Бізнес-логіка типу «не шли email якщо у користувача статус X». Це означає, що умова належить тому BC, який знає про статус (Auth / Billing). Notifications приймає event і шле — крапка
- ❌ Жорстке кодування шаблонів у `notifications/domain/`. Шаблони — конфіг або зберігаються в БД, але точно не в типах
