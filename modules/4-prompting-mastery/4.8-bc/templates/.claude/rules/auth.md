---
name: auth-bc-rules
description: Path-specific rules для Auth Bounded Context
paths:
  - "auth/**"
---

# Auth Bounded Context

Scope: реєстрація, логін, сесії, паролі. Все, що пов'язано з identity користувача — тут.

## Domain

Сутності: `User`, `Session`. `User.password_hash` — bcrypt-результат, ніколи не зберігаємо raw password.

Domain не знає про:
- HTTP (handlers — у `auth/infra/http/`, не імпортувати з domain)
- Postgres (repo interface у `auth/domain/`, реалізація у `auth/infra/postgres/`)
- Інші BC (`billing`, `commerce` etc) — комунікація через події

## Що Auth публікує (events)

- `UserRegistered { UserID, Email, RegisteredAt }` — Notifications підписується для welcome-email
- `UserLoggedIn { UserID, LoggedInAt }` — за потребою для analytics

## Що Auth споживає

Поки нічого. Auth — leaf BC, не залежить від інших.

## Anti-patterns у цьому BC

- ❌ Імпорт `billing/...` чи `notifications/...` напряму. Замість цього — публікуй event
- ❌ Класти HTTP-валідацію (формат email, довжина пароля) у `auth/domain/`. Domain валідує бізнес-інваріанти; HTTP-формат — у `auth/infra/http/dto.go`
- ❌ Зберігати пароль у `User.password` як plain string. Тільки `password_hash`
