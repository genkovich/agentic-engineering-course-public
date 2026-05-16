---
name: notifications-bc-rules
description: Rules for the Notifications Bounded Context (Python)
paths:
  - "app/notifications/**"
---

# Notifications BC

Scope: sending email / push / sms. Notifications is a sink BC — it only
listens to other BCs.

## Structure

```
app/notifications/
├── domain/
│   ├── notification.py         # Notification dataclass, Channel enum, Sender Protocol
│   ├── repository.py           # Repository Protocol
│   └── events.py               # placeholder for future NotificationSent etc
├── app/service.py              # Send use case
├── infra/
│   ├── postgres/notification_repo.py
│   ├── stub/sender.py          # StubSender — logs to stdout (demo)
│   ├── events/subscriber.py    # subscribes to UserRegistered, OrderPlaced, SubscriptionCreated
│   └── http/handler.py         # POST /notifications/test (manual trigger)
└── module.py
```

## Rules

- Domain does not import other BCs
- ❗ EXCEPTION: `app/notifications/infra/events/` is allowed to import
  other BCs' `domain` packages for event subscription. Documented in
  `importlinter.ini` (`independence` contract `ignore_imports`). Other
  parts of `app/notifications/infra/*` — not allowed
- `Sender` — Protocol in `domain/`. Concrete implementations in
  `infra/<provider>/` (currently only `stub/`)
- Production-grade adapters go in `infra/email/` (SMTP), `infra/push/`
  (APNS/FCM), `infra/sms/` (Twilio etc)

## Cross-BC interaction

Notifications listens to:
- `auth.UserRegistered` → welcome email
- `commerce.OrderPlaced` → order confirmation email
- `billing.SubscriptionCreated` → welcome letter

Notifications does not publish events at this stage.

## Anti-patterns

- ❌ Reentry: `notifications` calling `auth` / `billing` directly. It only listens
- ❌ Business logic like "do not send if user has status X" — that belongs
  in the BC that knows about the status. Notifications receives an event
  and sends — period
- ❌ Hard-coded templates in `domain/`. Templates live in config or DB
- ❌ Importing `app.auth.app.*` or `app.billing.app.*`. Only `domain` event
  types, only via `infra/events/`
