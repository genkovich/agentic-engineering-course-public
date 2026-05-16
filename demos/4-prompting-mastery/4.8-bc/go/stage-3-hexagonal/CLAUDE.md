# CLAUDE.md

Router-CLAUDE.md для stage-3-hexagonal. Конкретні правила для кожного BC живуть у `.claude/rules/<bc>.md` з frontmatter `paths:`.

## Architecture

Pattern: **Hexagonal per Bounded Context**.

5 BC: `auth/`, `catalog/`, `commerce/`, `billing/`, `notifications/`. Кожен — повний модуль `domain/`, `app/`, `infra/`.

```
<bc>/
├── domain/         # entities + interfaces (ports). Не імпортує net/http, БД, інші BC
├── app/            # use cases. Залежить тільки від <bc>/domain і shared/events
├── infra/
│   ├── postgres/   # adapter для repository port
│   └── http/       # HTTP handlers. dto.go, errors.go, handler.go
└── module.go       # self-wiring, повертає *Module з RouteRegistrar
```

## Dependency rule (hard, перевіряється `make arch-test`)

```
<bc>/domain   → nothing (тільки stdlib)
<bc>/app      → <bc>/domain, shared/events
<bc>/infra/*  → <bc>/domain, <bc>/app, shared/*
main          → all <bc>/module, shared/server, shared/events
```

**NEVER:**
- `<bc>/domain` імпортує `net/http`, `pgxpool`, або будь-що з `<bc>/infra`
- BC `auth` імпортує BC `billing` напряму (порушує BC isolation — комунікація через `shared/events`)
- `shared/` імпортує конкретний BC

**Виняток:** `notifications/infra/events/` має право імпортувати `<other-bc>/domain` для event subscription. Це задокументовано в `.arch-lint.yml`.

## Cross-BC комунікація

Тільки через `shared/events.Bus`. Кожен BC публікує власні `domain.<EventName>` типи; інші підписуються в своєму `infra/events/`.

```
auth.UserRegistered      → notifications підписаний (welcome email)
commerce.OrderPlaced     → notifications, billing підписані
billing.SubscriptionCreated → notifications підписаний
```

## Workflow

1. **Визначити BC.** Фіча про що — Notifications? Billing? Auth? Якщо торкається 2+ BC — окремі задачі з координацією через події
2. **Створити domain entity / event.** Типи й interface у `<bc>/domain/`. Без HTTP, без БД
3. **Написати use case.** `<bc>/app/service.go`, тільки через interfaces
4. **Додати infra adapter.** `<bc>/infra/postgres/` для БД, `<bc>/infra/http/` для handlers
5. **Запустити arch-test.** `make arch-test` має пройти
6. **PR.** Якщо торкає тільки один BC — все правильно

## Path-specific rules

- `auth/**` → `.claude/rules/auth.md`
- `catalog/**` → `.claude/rules/catalog.md`
- `commerce/**` → `.claude/rules/commerce.md`
- `billing/**` → `.claude/rules/billing.md`
- `notifications/**` → `.claude/rules/notifications.md`

## Conventions

- All code in English. Comments українською дозволені для бізнес-логіки
- Conventional commits: `feat(<bc>): ...`, `fix(<bc>): ...`. BC у scope.
- One BC per PR. Cross-BC зміни — окремі PR з координацією через події
- `make arch-test` перед кожним PR. Failing arch-test блокує merge у CI

## Як перевірити

```bash
make db-up
make db-migrate
make run            # окремий термінал
make smoke          # 6 endpoints → all 200/201
make arch-test      # ✓ No violations found
```
