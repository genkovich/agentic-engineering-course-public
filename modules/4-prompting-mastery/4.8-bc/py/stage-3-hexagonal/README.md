# Python stage-3-hexagonal

**Hexagonal per BC.** 5 Bounded Contexts, кожен — окремий модуль з
`domain/app/infra/`. `make arch-test` через `import-linter` v2 ловить
порушення меж. CLAUDE.md і `.claude/rules/` дають Claude карту BC і scoped
правила.

Це фінальна стадія зрілості зі Slide 7 лекції.

## Стек

- Python 3.12–3.14
- FastAPI 0.110+ (async)
- SQLAlchemy 2.x з **asyncpg** (async driver)
- Alembic 1.13+ — 5 окремих revisions, по одній на BC, з префіксом таблиць
- Postgres 18 у Docker
- `bcrypt` — паролі
- `import-linter` v2 — архітектурні тести (independence + per-BC layers)
- In-memory event bus у `app/shared/events.py` — cross-BC комунікація без брокера

## Структура

```
stage-3-hexagonal/
├── pyproject.toml
├── docker-compose.yml
├── Makefile                     # smoke, arch-test, db-up, db-migrate, run
├── README.md
├── .env.example
├── alembic.ini
├── .importlinter                # contracts: independence + 5 layers contracts
├── CLAUDE.md                    # router-CLAUDE.md з BC structure rules
├── ARCHITECTURE.md              # mermaid BC Map (5 BC, 4 events)
├── .github/workflows/ci.yml     # py compile + arch-test у CI
├── .claude/rules/               # path-specific rules per BC
│   ├── auth.md
│   ├── catalog.md
│   ├── commerce.md
│   ├── billing.md
│   └── notifications.md
├── migrations/                  # Alembic, одна revision на BC
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_auth.py
│       ├── 0002_catalog.py
│       ├── 0003_commerce.py
│       ├── 0004_billing.py
│       └── 0005_notifications.py
├── scripts/smoke.sh
└── app/
    ├── main.py                  # wires modules → FastAPI
    ├── shared/
    │   ├── apperr.py            # AppError dataclass
    │   ├── httputil.py          # to_http_exception
    │   ├── events.py            # Event base, EventBus
    │   └── db.py                # async engine + SessionMaker
    ├── auth/
    │   ├── domain/              # User, UserRegistered, UserRepository (Protocol), errors
    │   ├── app/service.py       # Register, Login
    │   ├── infra/
    │   │   ├── postgres/user_repo.py
    │   │   └── http/            # handler.py, dto.py, errors.py
    │   └── module.py            # New(SessionMaker, bus) → Module
    ├── catalog/                 # similar shape
    ├── commerce/                # similar
    ├── billing/                 # similar
    └── notifications/
        ├── domain/              # Notification, Channel enum, Sender (Protocol), Repository, events
        ├── app/service.py       # Send use case
        ├── infra/
        │   ├── postgres/notification_repo.py
        │   ├── stub/sender.py            # StubSender (логи у stdout)
        │   ├── events/subscriber.py      # підписки на UserRegistered, OrderPlaced, SubscriptionCreated
        │   └── http/handler.py           # POST /notifications/test
        └── module.py
```

## Швидкий старт

```bash
python3 -m venv .venv
source .venv/bin/activate     # Windows (Git Bash): source .venv/Scripts/activate
make doctor                   # перевірка: docker, python, активний venv, вільні порти
make install                  # залежності з requirements.lock.txt
make db-up
make db-migrate
make run                      # в ОКРЕМОМУ терміналі — процес не завершується
make smoke                    # 6 endpoints → all 2xx
make arch-test                # Contracts: 6 kept, 0 broken
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
auth.UserRegistered           → notifications  (welcome email)
commerce.OrderPlaced          → notifications  (order confirmation)
billing.SubscriptionCreated   → notifications  (welcome letter)
```

Жоден BC не імпортує іншого напряму — тільки через `app/shared/events.EventBus`.
Виняток — `app/notifications/infra/events/subscriber.py`, який мусить знати
domain types усіх відправників. Виняток задокументовано у `.importlinter`.

## Arch-test — як це працює

```bash
make arch-test
```

`import-linter` парсить імпорти і перевіряє граф залежностей проти
`.importlinter`:

- `independence` контракт — `app.auth`, `app.catalog`, `app.commerce`,
  `app.billing`, `app.notifications` не імпортують одне одного (за винятком
  `app.notifications.infra.events.* -> app.<other-bc>.domain.*`)
- 5 окремих `layers` контрактів — у кожному BC `infra` -> `app` -> `domain`,
  без зворотніх імпортів

### Спробуй зламати

```python
# у app/auth/app/service.py додай
from app.billing.domain.subscription import Subscription   # noqa: F401
```

Запусти `make arch-test` — побачиш помилку про `independence` контракт між
`app.auth` і `app.billing`. Прибери імпорт — `make arch-test` знову проходить.

Це і є демонстрація скринкаста 4.

## CLAUDE.md і scoped rules

Коли Claude читає файли з `app/auth/...`, автоматично підтягується
`.claude/rules/auth.md` з BC-specific правилами. Це той самий патерн, що в
лекції 4.5 (Claude Code Rules) — тільки `paths:` мапляться на BC, не на
frontend/backend/infra.

Спробуй: відкрий `claude` у цій папці, попроси «додай endpoint
POST /notifications/welcome що шле email». Очікуваний артефакт — Claude:
1. Створює файл у `app/notifications/infra/http/`, не у `app/main.py` чи
   `app/shared/`
2. Реюзає `app/notifications/app/service.py` (`svc.send`)
3. Не імпортує `app.auth.*` напряму

Це і є кульмінація лекції — Claude слідує BC-структурі, бо вона
матеріалізована у файлах + правилах + arch-test.

## Сцени для скринкастів

- **Скринкаст 1:** Той самий промпт «куди покласти welcome-email» → одна
  однозначна відповідь (`app/notifications/app/service.py`)
- **Скринкаст 3:** `tree -L 3 app/notifications/` → повна hexagonal структура
- **Скринкаст 4:** Демо arch-test (зламати → виправити). Дивись «Спробуй зламати»
- **Скринкаст 5:** Claude генерує endpoint у правильний BC автоматично
- **Скринкаст 6:** ARCHITECTURE.md з mermaid BC Map — додати `reviews/` BC,
  ноду в граф, дві стрілки подій

Точні промпти і очікувані артефакти — у [`../../screencast-prompts.md`](../../screencast-prompts.md).
