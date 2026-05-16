---
name: auth-bc-rules
description: Rules для Auth Bounded Context
paths:
  - "auth/**"
---

# Auth BC

Scope: реєстрація, логін, паролі. Identity користувача.

## Структура

```
auth/
├── domain/
│   ├── user.go           # User entity, UserRegistered event
│   ├── repository.go     # UserRepository interface (port)
│   └── errors.go         # ErrInvalidCredentials, ErrEmailAlreadyExists, ErrUserNotFound
├── app/service.go        # Register, Login use cases
├── infra/
│   ├── postgres/repo.go  # UserRepo implements UserRepository
│   └── http/             # handler.go, dto.go, errors.go
└── module.go
```

## Правила

- Domain не імпортує `net/http`, `pgxpool`, інші BC
- Паролі — `bcrypt`, ніколи raw
- Sentinel errors у domain (`errors.New("auth.invalid_credentials")` тощо)
- Ports мапить domain errors на `shared/apperr.Error{Code, Message, StatusCode}`
- Event publishing: `service.Register` → `bus.Publish(UserRegistered{...})`

## Anti-patterns

- ❌ Імпорт `billing/...`, `notifications/...` напряму. Замість цього — публікуй event
- ❌ HTTP-валідація (формат email) у domain. Це `infra/http/dto.go`
- ❌ Зберігання raw `password` у `User`. Тільки `password_hash`
