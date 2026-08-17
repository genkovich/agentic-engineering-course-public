# TS stage-3-hexagonal

**Hexagonal per BC.** 5 Bounded Contexts, кожен — окремий модуль з `domain/app/infra/`. `make arch-test` ловить порушення меж через `dependency-cruiser`. CLAUDE.md і `.claude/rules/` дають Claude карту BC і scoped правила.

Це фінальна стадія зрілості зі Slide 7 лекції. Сюди приходять, коли домен реально складний і команда більше однієї людини.

## Стек

- Node.js 22+
- Fastify 4 — HTTP сервер
- pg — Postgres драйвер (raw SQL)
- bcryptjs — паролі
- TypeScript 5 + tsx (dev) / `tsc` (build)
- Postgres 18 у Docker
- `dependency-cruiser` v16 — архітектурні тести
- In-memory event bus у `src/shared/events/bus.ts` — cross-BC комунікація без брокера

## Структура

```
stage-3-hexagonal/
├── package.json
├── tsconfig.json
├── docker-compose.yml
├── Makefile                        # smoke, arch-test, db-up, db-migrate, build
├── .env.example
├── .dependency-cruiser.cjs         # forbidden rules для arch-test
├── .github/workflows/ci.yml        # typecheck + arch-test у CI
├── ARCHITECTURE.md                 # mermaid BC Map (5 BC, 4 events)
├── CLAUDE.md                       # router-CLAUDE.md з BC structure rules
├── README.md
├── .claude/rules/                  # path-specific rules per BC
│   ├── auth.md
│   ├── catalog.md
│   ├── commerce.md
│   ├── billing.md
│   └── notifications.md
├── migrations/                     # один SQL на BC
│   ├── 0001_auth.sql
│   ├── 0002_catalog.sql
│   ├── 0003_commerce.sql
│   ├── 0004_billing.sql
│   └── 0005_notifications.sql
├── scripts/smoke.sh
└── src/
    ├── index.ts                    # bootstrap: wires modules
    ├── shared/
    │   ├── db.ts                   # postgres pool
    │   ├── apperr.ts               # AppError {code, message, statusCode}
    │   ├── httputil.ts             # writeError + AppError mapping
    │   └── events/bus.ts           # in-memory pub/sub EventBus
    ├── auth/
    │   ├── domain/
    │   │   ├── user.ts             # User, UserRegistered event
    │   │   ├── repository.ts       # UserRepository interface (port)
    │   │   └── errors.ts
    │   ├── app/service.ts          # register, login
    │   ├── infra/
    │   │   ├── postgres/userRepo.ts
    │   │   └── http/               # handler.ts, dto.ts, errors.ts
    │   └── module.ts               # newModule(db, bus) → Module
    ├── catalog/                    # similar shape
    ├── commerce/                   # similar
    ├── billing/                    # similar
    └── notifications/
        ├── domain/
        │   ├── notification.ts     # Notification, Channel, Sender (port), Repository
        │   ├── repository.ts
        │   └── events.ts           # (порожньо)
        ├── app/service.ts          # send use case
        ├── infra/
        │   ├── postgres/notificationRepo.ts
        │   ├── stub/sender.ts      # demo Sender (логи у stdout)
        │   ├── events/subscriber.ts # підписки на UserRegistered/OrderPlaced/SubscriptionCreated
        │   └── http/handler.ts     # POST /notifications/test
        └── module.ts
```

## Швидкий старт

```bash
make doctor                   # перевірка: docker, node, вільні порти
make install                  # npm ci строго за package-lock.json
make db-up
make db-migrate
make run                      # в ОКРЕМОМУ терміналі — процес не завершується
make smoke                    # 6 endpoints → all 2xx
make arch-test                # ✓ no dependency violations found
make clean                    # зупинити базу і видалити том
```

Порт 5432 або 8080 зайнятий? Візьми інші — `make db-up PGPORT=5433`, `make run HTTP_PORT=8081`
(і тоді `make smoke BASE_URL=http://localhost:8081`). Постійний варіант — `cp .env.example .env`.

Щось не сходиться — [`TROUBLESHOOTING.md`](../../TROUBLESHOOTING.md).
## Ендпоінти

- `POST /auth/register`
- `POST /auth/login`
- `GET  /products`
- `POST /orders` — публікує `commerce.OrderPlaced` → notifications підписаний
- `POST /subscriptions` — публікує `billing.SubscriptionCreated` → notifications підписаний
- `POST /notifications/test` — manual trigger

## Cross-BC events (in-memory bus)

```
auth.UserRegistered          → notifications  (welcome email)
commerce.OrderPlaced         → notifications  (order confirmation)
billing.SubscriptionCreated  → notifications  (welcome letter)
```

Жоден BC не імпортує іншого напряму — тільки через `shared/events.EventBus`. Виняток — `src/notifications/infra/events/subscriber.ts`, який мусить знати domain types усіх відправників. Виняток задокументовано у `.dependency-cruiser.cjs` (rule `events-only-foreign-domain`).

## Arch-test — як це працює

```bash
make arch-test
```

`dependency-cruiser` парсить імпорти і перевіряє граф залежностей проти `.dependency-cruiser.cjs`. Якщо `src/auth/app/` починає імпортувати `src/billing/domain/` — падає з конкретним рядком rule `no-cross-context`.

### Спробуй зламати

```ts
// у src/auth/app/service.ts додай
import type { Subscription } from "../../billing/domain/subscription.js";
```

Запусти `make arch-test` — побачиш помилку з вказівкою на rule `no-cross-context`. Прибери імпорт — `make arch-test` знову проходить.

Це і є демонстрація скринкаста 4.

## CLAUDE.md і scoped rules

Коли Claude читає файли з `src/auth/...`, автоматично підтягується `.claude/rules/auth.md` з BC-specific правилами. Це той самий патерн, що в лекції 4.5 (Claude Code Rules) — тільки `paths:` мапяться на BC, не на frontend/backend/infra.

Спробуй: відкрий `claude` у цій папці, попроси «додай endpoint POST /notifications/welcome що шле email». Очікуваний артефакт — Claude:
1. Створює файл у `src/notifications/infra/http/`, не у `src/index.ts` чи `src/shared/`
2. Реюзає `src/notifications/app/service.ts` (`Service.send`)
3. Не імпортує `src/auth/...` напряму

Це і є кульмінація лекції — Claude слідує BC-структурі, бо вона матеріалізована у файлах + правилах + arch-test.

## Сцени для скринкастів

- **Скринкаст 4 (TS):** Демо arch-test (зламати → виправити). Дивись секцію «Arch-test — як це працює»
