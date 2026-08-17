---
name: auth-bc-rules
description: Rules for the Auth Bounded Context (Python)
paths:
  - "app/auth/**"
---

# Auth BC

Scope: registration, login, password hashing. User identity.

## Structure

```
app/auth/
├── domain/
│   ├── user.py             # User dataclass, UserRegistered event
│   ├── repository.py       # UserRepository Protocol (port)
│   └── errors.py           # InvalidCredentialsError, EmailAlreadyExistsError, UserNotFoundError
├── app/service.py          # Register, Login use cases
├── infra/
│   ├── postgres/user_repo.py    # UserRepo implements UserRepository
│   └── http/                    # handler.py (build_router), dto.py, errors.py
└── module.py               # self-wiring → Module with routes()
```

## Rules

- Domain does not import `fastapi`, `sqlalchemy`, or other BCs
- Passwords — `bcrypt`, never raw
- Sentinel exceptions in domain (`InvalidCredentialsError` etc), all
  inheriting from `AuthDomainError`
- HTTP layer maps domain errors to `shared.apperr.AppError` via
  `infra/http/errors.py`
- Event publishing: `Service.register` → `bus.publish(UserRegistered(...))`

## Anti-patterns

- ❌ Importing `app.billing.*`, `app.notifications.*` directly. Publish an event instead
- ❌ HTTP-level validation (email format) in domain. That belongs in `infra/http/dto.py`
- ❌ Storing raw `password` on `User`. Only `password_hash`
