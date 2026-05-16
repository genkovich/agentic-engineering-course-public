# CLAUDE.md

Router-CLAUDE.md для stage-3-hexagonal (TypeScript). Конкретні правила для кожного BC живуть у `.claude/rules/<bc>.md` з frontmatter `paths:`.

## Architecture

Pattern: **Hexagonal per Bounded Context**.

5 BC: `src/auth/`, `src/catalog/`, `src/commerce/`, `src/billing/`, `src/notifications/`. Кожен — повний модуль `domain/`, `app/`, `infra/`.

```
src/<bc>/
├── domain/         # entities + interfaces (ports). Не імпортує fastify, БД, інші BC
├── app/            # use cases. Залежить тільки від <bc>/domain і shared/events
├── infra/
│   ├── postgres/   # adapter для repository port
│   └── http/       # Fastify handlers, dto.ts, errors.ts
└── module.ts       # self-wiring, повертає Module з handler
```

## Dependency rule (hard, перевіряється `make arch-test`)

```
<bc>/domain   → nothing (тільки stdlib, shared/events для event types)
<bc>/app      → <bc>/domain, shared/events
<bc>/infra/*  → <bc>/domain, <bc>/app, shared/*
src/index.ts  → all <bc>/module, shared/db, shared/events
```

**NEVER:**
- `<bc>/domain` імпортує `fastify`, `pg`, або будь-що з `<bc>/infra`
- BC `auth` імпортує BC `billing` напряму (порушує BC isolation — комунікація через `shared/events`)
- `shared/` імпортує конкретний BC

**Виняток:** `notifications/infra/events/` має право імпортувати `<other-bc>/domain` для event subscription. Це задокументовано в `.dependency-cruiser.cjs` (`events-only-foreign-domain` rule).

## Cross-BC комунікація

Тільки через `shared/events.EventBus`. Кожен BC публікує власні `domain.<EventName>` класи з полем `.name`; інші підписуються в своєму `infra/events/`.

```
auth.UserRegistered          → notifications підписаний (welcome email)
commerce.OrderPlaced         → notifications підписаний (order confirmation)
billing.SubscriptionCreated  → notifications підписаний (welcome letter)
```

## Workflow

1. **Визначити BC.** Фіча про що — Notifications? Billing? Auth? Якщо торкається 2+ BC — окремі задачі з координацією через події
2. **Створити domain entity / event.** Типи й interface у `<bc>/domain/`. Без HTTP, без БД
3. **Написати use case.** `<bc>/app/service.ts`, тільки через interfaces
4. **Додати infra adapter.** `<bc>/infra/postgres/` для БД, `<bc>/infra/http/` для handlers
5. **Запустити arch-test.** `make arch-test` має пройти
6. **PR.** Якщо торкає тільки один BC — все правильно

## Path-specific rules

- `src/auth/**` → `.claude/rules/auth.md`
- `src/catalog/**` → `.claude/rules/catalog.md`
- `src/commerce/**` → `.claude/rules/commerce.md`
- `src/billing/**` → `.claude/rules/billing.md`
- `src/notifications/**` → `.claude/rules/notifications.md`

## Conventions

- All code in English. Comments українською дозволені для бізнес-логіки
- Conventional commits: `feat(<bc>): ...`, `fix(<bc>): ...`. BC у scope.
- One BC per PR. Cross-BC зміни — окремі PR з координацією через події
- `make arch-test` перед кожним PR. Failing arch-test блокує merge у CI
- TS: `interface` для ports і entity-структур; `class` тільки коли треба інстанс з методами (Service, Handler, repo impl, event types)

## Як перевірити

```bash
npm install
make db-up
make db-migrate
make run            # окремий термінал
make smoke          # 6 endpoints → all 200/201
make arch-test      # ✓ no dependency violations found
```
