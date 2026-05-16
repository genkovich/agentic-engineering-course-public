---
name: auth-bc-rules
description: Rules для Auth Bounded Context
paths:
  - "src/auth/**"
---

# Auth BC

Scope: реєстрація, логін, паролі. Identity користувача.

## Структура

```
src/auth/
├── domain/
│   ├── user.ts           # User type, UserRegistered event
│   ├── repository.ts     # UserRepository interface (port)
│   └── errors.ts         # InvalidCredentialsError, EmailAlreadyExistsError, UserNotFoundError
├── app/service.ts        # Register, Login use cases
├── infra/
│   ├── postgres/userRepo.ts  # PgUserRepo implements UserRepository
│   └── http/                 # handler.ts, dto.ts, errors.ts
└── module.ts
```

## Правила

- Domain не імпортує `fastify`, `pg`, інші BC
- Паролі — `bcryptjs.hash`, ніколи raw
- Sentinel errors у domain (наприклад `InvalidCredentialsError`)
- Ports мапить domain errors на `shared/apperr.AppError({code, message, statusCode})` через `infra/http/errors.ts`
- Event publishing: `Service.register` → `bus.publish(new UserRegistered(...))`

## Anti-patterns

- ❌ Імпорт `src/billing/...`, `src/notifications/...` напряму. Замість цього — публікуй event
- ❌ HTTP-валідація (формат email) у domain. Це `infra/http/handler.ts` або `dto.ts`
- ❌ Зберігання raw `password` у `User`. Тільки `passwordHash`
