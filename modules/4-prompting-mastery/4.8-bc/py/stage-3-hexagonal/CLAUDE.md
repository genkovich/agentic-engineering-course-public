# CLAUDE.md

Router-CLAUDE.md for stage-3-hexagonal (Python). BC-specific rules live in
`.claude/rules/<bc>.md` with `paths:` frontmatter.

## Architecture

Pattern: **Hexagonal per Bounded Context**.

5 BCs: `app/auth/`, `app/catalog/`, `app/commerce/`, `app/billing/`,
`app/notifications/`. Each is a full module with `domain/`, `app/`, `infra/`.

```
app/<bc>/
├── domain/         # entities + Protocols (ports). No fastapi, no asyncpg, no other BCs
├── app/            # use cases. Depends only on <bc>/domain and shared/events
├── infra/
│   ├── postgres/   # adapter for repository port
│   └── http/       # FastAPI handler (build_router), dto.py, errors.py
└── module.py       # self-wiring → Module with routes()
```

## Dependency rule (hard, checked by `make arch-test`)

```
<bc>/domain   → only stdlib + shared/events.Event
<bc>/app      → <bc>/domain, shared/events
<bc>/infra/*  → <bc>/domain, <bc>/app, shared/*
main          → all <bc>/module, shared/*
```

**NEVER:**
- `<bc>/domain` imports `fastapi`, `sqlalchemy`, or anything from `<bc>/infra`
- BC `auth` imports BC `billing` directly (BC isolation — communicate via
  `shared/events`)
- `shared/` imports a specific BC

**Exception:** `notifications/infra/events/` is allowed to import other BCs'
`domain` modules for event subscription. Documented in `.importlinter`.

## Cross-BC communication

Only via `shared/events.EventBus`. Each BC publishes its own
`domain.<EventName>` types; others subscribe in their `infra/events/`.

```
auth.UserRegistered           → notifications subscribed (welcome email)
commerce.OrderPlaced          → notifications subscribed
billing.SubscriptionCreated   → notifications subscribed
```

## Tooling

- **Python 3.12** + FastAPI 0.110+
- **SQLAlchemy 2.x async** + asyncpg (no sync drivers anywhere except Alembic env)
- **Alembic 1.13+** — 5 revisions, one per BC, BC-prefixed tables
- **import-linter v2** — `lint-imports` (конфіг `.importlinter` знаходиться автоматично)
- **Postgres 18** in docker-compose
- **bcrypt** for passwords

## Workflow

1. **Identify the BC.** Auth? Billing? Notifications? If 2+ BCs are touched,
   split into separate tasks coordinated via events.
2. **Domain entity / event.** Types and Protocols in `app/<bc>/domain/`. No HTTP, no DB.
3. **Use case.** `app/<bc>/app/service.py`. Depends only on `domain` + `shared/events`.
4. **Infra adapter.** `app/<bc>/infra/postgres/` for DB, `app/<bc>/infra/http/` for handlers.
5. **arch-test.** `make arch-test` must pass.
6. **PR.** If only one BC is touched — you did it right.

## Path-specific rules

- `app/auth/**` → `.claude/rules/auth.md`
- `app/catalog/**` → `.claude/rules/catalog.md`
- `app/commerce/**` → `.claude/rules/commerce.md`
- `app/billing/**` → `.claude/rules/billing.md`
- `app/notifications/**` → `.claude/rules/notifications.md`

## Conventions

- All code in English. Comments in Ukrainian allowed for business logic
- Conventional commits: `feat(<bc>): ...`, `fix(<bc>): ...`. BC in scope.
- One BC per PR. Cross-BC changes — separate PRs coordinated via events.
- `make arch-test` before every PR. Failing arch-test blocks merge in CI.

## How to verify

```bash
pip install -e .
make db-up
make db-migrate
make run             # separate terminal
make smoke           # 6 endpoints → all 200/201
make arch-lint-install   # one-off
make arch-test       # ✓ All contracts kept
```
