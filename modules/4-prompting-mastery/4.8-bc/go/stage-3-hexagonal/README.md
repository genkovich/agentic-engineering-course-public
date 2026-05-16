# Go stage-3-hexagonal

**Hexagonal per BC.** 5 Bounded Contexts, кожен — окремий модуль з `domain/app/infra/`. `make arch-test` ловить порушення меж. CLAUDE.md і `.claude/rules/` дають Claude карту BC і scoped правила.

Це фінальна стадія зрілості зі Slide 7 лекції. Сюди приходять, коли домен реально складний і команда більше однієї людини.

## Стек

- Go 1.24
- chi/v5 — роутинг
- pgx/v5 — Postgres
- Postgres 18 у Docker
- bcrypt — паролі
- `go-arch-lint` v1.11.5 — архітектурні тести
- In-memory event bus у `shared/events/` — cross-BC комунікація без брокера

## Структура

```
stage-3-hexagonal/
├── main.go                      # wires modules through ports/registrar
├── go.mod
├── docker-compose.yml
├── Makefile                     # smoke, arch-test, db-up, db-migrate, build
├── .env.example
├── .arch-lint.yml               # contracts для go-arch-lint
├── .github/workflows/ci.yml     # build + arch-test у CI
├── ARCHITECTURE.md              # mermaid BC Map (5 BC, 4 events)
├── CLAUDE.md                    # router-CLAUDE.md з BC structure rules
├── README.md
├── .claude/rules/               # path-specific rules per BC
│   ├── auth.md
│   ├── catalog.md
│   ├── commerce.md
│   ├── billing.md
│   └── notifications.md
├── migrations/                  # один SQL на BC
│   ├── 0001_auth.sql
│   ├── 0002_catalog.sql
│   ├── 0003_commerce.sql
│   ├── 0004_billing.sql
│   └── 0005_notifications.sql
├── scripts/smoke.sh
├── shared/
│   ├── apperr/apperr.go         # типізовані помилки {Code, Message, StatusCode}
│   ├── httputil/json.go         # JSON write + error mapping
│   ├── events/bus.go            # in-memory pub/sub Bus
│   └── server/registrar.go      # RouteRegistrar interface
├── auth/
│   ├── domain/                  # User, UserRegistered event, UserRepository, errors
│   ├── app/service.go           # Register, Login
│   ├── infra/
│   │   ├── postgres/repo.go     # PgUserRepo implements UserRepository
│   │   └── http/                # handler.go, dto.go, errors.go
│   └── module.go                # auth.New(db, bus) → *Module
├── catalog/                     # similar shape
├── commerce/                    # similar
├── billing/                     # similar
└── notifications/
    ├── domain/notification.go   # Notification, Channel, Sender (port), Repository
    ├── app/service.go           # Send use case
    ├── infra/
    │   ├── postgres/repo.go
    │   ├── stub/sender.go       # demo Sender (логи у stdout)
    │   ├── events/subscriber.go # підписки на UserRegistered/OrderPlaced/SubscriptionCreated
    │   └── http/handler.go      # POST /notifications/test
    └── module.go
```

## Швидкий старт

```bash
make db-up
make db-migrate
make run                      # окремий термінал
make smoke                    # 6 endpoints → all 2xx
make arch-lint-install        # одноразово, ~10 секунд
make arch-test                # ✓ No violations found
```

## Ендпоінти

- `POST /auth/register`
- `POST /auth/login`
- `GET  /products`
- `POST /orders` — публікує `commerce.OrderPlaced` → notifications, billing підписані
- `POST /subscriptions` — публікує `billing.SubscriptionCreated` → notifications підписаний
- `POST /notifications/test` — manual trigger

## Cross-BC events (in-memory bus)

```
auth.UserRegistered          → notifications  (welcome email)
commerce.OrderPlaced         → notifications  (order confirmation)
commerce.OrderPlaced         → billing        (create invoice — не реалізовано в демо, тільки subscription наразі)
billing.SubscriptionCreated  → notifications  (welcome letter)
```

Жоден BC не імпортує іншого напряму — тільки через `shared/events.Bus`. Виняток — `notifications/infra/events/subscriber.go`, який мусить знати domain types усіх відправників. Виняток задокументовано у `.arch-lint.yml`.

## Arch-test — як це працює

```bash
make arch-test
```

`go-arch-lint` парсить імпорти і перевіряє граф залежностей проти `.arch-lint.yml`. Якщо `auth/app/` починає імпортувати `billing/domain/` — падає з конкретним рядком.

### Спробуй зламати

```go
// у auth/app/service.go додай
import billingdomain "github.com/genkovich/.../billing/domain"
```

Запусти `make arch-test` — побачиш помилку з вказівкою на `auth-app` як component, який не може залежати від `billing-domain`. Прибери імпорт — `make arch-test` знову проходить.

Це і є демонстрація скринкаста 4.

## CLAUDE.md і scoped rules

Коли Claude читає файли з `auth/...`, автоматично підтягується `.claude/rules/auth.md` з BC-specific правилами. Це той самий патерн, що в лекції 4.5 (Claude Code Rules) — тільки `paths:` мапяться на BC, не на frontend/backend/infra.

Спробуй: відкрий `claude` у цій папці, попроси «додай endpoint POST /notifications/welcome що шле email». Очікуваний артефакт — Claude:
1. Створює файл у `notifications/infra/http/`, не у `main.go` чи `shared/`
2. Реюзає `notifications/app/service.go` (`svc.Send`)
3. Не імпортує `auth/...` напряму

Це і є кульмінація лекції — Claude слідує BC-структурі, бо вона матеріалізована у файлах + правилах + arch-test.

## Сцени для скринкастів

- **Скринкаст 1:** Той самий промпт «куди покласти welcome-email» → одна однозначна відповідь (`notifications/app/service.go`)
- **Скринкаст 3:** `tree -L 3 notifications/` → повна hexagonal структура
- **Скринкаст 4:** Демо arch-test (зламати → виправити). Дивись секцію «Arch-test — як це працює»
- **Скринкаст 5:** Claude генерує endpoint у правильний BC автоматично
- **Скринкаст 6:** ARCHITECTURE.md з mermaid BC Map — додати `reviews/` BC, ноду в граф, дві стрілки подій

Точні промпти і очікувані артефакти — у [`../screencast-prompts.md`](../screencast-prompts.md).
