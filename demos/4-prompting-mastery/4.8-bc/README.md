# 4.8-bc — Bounded Contexts

Демо для лекції **4.8 Bounded Contexts** курсу _Agentic Engineering з Claude_. Один і той самий e-commerce домен реалізований на 3 мовах × 3 рівнях зрілості структури = 9 робочих проектів.

Лекція тут: `Own Brand/AI Course/Claude Course/Module 4/4.8 Bounded Contexts/` (Obsidian).

## Матриця: 3 мови × 3 стейджі

| Папка | Стек | Stage 1 | Stage 2 | Stage 3 | Скринкасти |
|---|---|---|---|---|---|
| [`go/`](./go) | Go 1.26 + chi/v5 + pgx | flat | feature-first | hexagonal + `go-arch-lint` | 1, 2, 3, 4, 5, 6 |
| [`ts/`](./ts) | Node 22 + Fastify + Knex | flat | feature-first | hexagonal + `dependency-cruiser` | 4 |
| [`py/`](./py) | Python 3.12 + FastAPI + SQLAlchemy | flat | feature-first | hexagonal + `import-linter` | 4 |

**Reference мова — Go.** TS і Py точно дзеркалять домен, ендпоінти і структуру каталогів. Скринкасти 1–3, 5, 6 знімаються на Go; скринкаст 4 показує arch-test послідовно у Go → TS → Py.

## Стадії зрілості

| Стадія | Папка | Що показує |
|---|---|---|
| **Stage 1 — Flat** | `<lang>/stage-1-flat/` | `handler/service/repo` плоско, без BC. ~10–15 файлів. BC існує тільки в голові |
| **Stage 2 — Feature-first** | `<lang>/stage-2-feature-first/` | 5 BC у вигляді vertical slice (одна папка на BC, всередині handler/service/repo разом). ~25–30 файлів |
| **Stage 3 — Hexagonal** | `<lang>/stage-3-hexagonal/` | Кожен BC — повний `domain/app/infra` з ports & adapters, `.arch-lint.yml` (або еквівалент), CI з arch-test, `CLAUDE.md`, `ARCHITECTURE.md` з mermaid BC Map. ~50–60 файлів |

## Домен (єдиний для всіх 9 проектів)

E-commerce з **5 Bounded Contexts**:
- **Auth** — реєстрація, логін, сесії
- **Catalog** — продукти, категорії
- **Commerce** — кошик, замовлення
- **Billing** — підписки, оплата
- **Notifications** — email / push доставка

### Сутності
- `User { id uuid, email string, password_hash string, created_at }`
- `Product { id uuid, name string, price_cents int64, category_id uuid }`
- `Order { id uuid, user_id uuid, items, total_cents int64, status string }`
- `Subscription { id uuid, user_id uuid, plan string, next_charge_at time }`
- `Notification { id uuid, user_id uuid, channel string, payload string, sent_at *time }`

### Ендпоінти (однакові у всіх 9 проектах)
- `POST /auth/register` — реєстрація
- `POST /auth/login` — логін
- `GET  /products` — каталог
- `POST /orders` — створення замовлення
- `POST /subscriptions` — оформлення підписки
- `POST /notifications/test` — тестова нотифікація (головний endpoint скринкаста 5)

## Швидкий старт

```bash
# Go reference
cd 4.8-bc/go/stage-3-hexagonal
docker compose up -d
make db-migrate
make smoke         # 6 endpoints → all 200
make arch-test     # ✓ No violations found
docker compose down -v
```

Аналогічно для `ts/` і `py/`. У stage-1 немає `make arch-test` — додається тільки в stage-3.

## Скринкасти лекції 4.8

| # | Тема | Папка для запуску |
|---|---|---|
| 1 | Той самий промпт, дві різні структури | `go/stage-1-flat` потім `go/stage-3-hexagonal` |
| 2 | Event Storming lite — від постітів до папок | `go/stage-2-feature-first` |
| 3 | Три плани папок — еволюція тієї самої фічі | `go/stage-1-flat` + `stage-2-feature-first` + `stage-3-hexagonal` (3 термінали) |
| 4 | Arch-test ловить порушення — Go / TS / Py | `go/stage-3-hexagonal` → `ts/stage-3-hexagonal` → `py/stage-3-hexagonal` |
| 5 | AI кладе код у правильне BC — кульмінація | `go/stage-3-hexagonal` |
| 6 | BC Map як живий документ | `go/stage-3-hexagonal` (`ARCHITECTURE.md`) |

Точні промпти з кожного скринкаста — у [`screencast-prompts.md`](./screencast-prompts.md).

## Шаблони

`templates/` містить:
- `CLAUDE.md.template` — заготовка для router-CLAUDE.md з BC structure rules
- `ARCHITECTURE.md.template` — заготовка для BC Map з mermaid
- `.claude/rules/` — приклади path-specific rules per BC (`auth.md`, `billing.md`, `notifications.md`)

Це referenсе для того, як виглядає stage-3 готовий до AI. Беремо як стартову точку для нового проекту і адаптуємо під свій домен.

## Що цей репо інтенційно НЕ містить

- Production-grade auth (JWT signing, refresh tokens, RBAC) — мінімальна реєстрація / логін достатньо щоб показати BC
- Реальні платіжні провайдери — Billing працює з in-memory mock-ом
- Frontend — це backend демо, фронт не релевантний
- Повне покриття тестами — є smoke + arch-test, юніти не пріоритет
