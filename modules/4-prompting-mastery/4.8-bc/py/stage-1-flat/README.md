# Python stage-1-flat

**Layered (handler/service/repo) without Bounded Contexts.** BC існує лише в голові команди — у файлах розкидані функції по шарах.

Це навмисно нечітка структура. Лекційний промпт «куди мені покласти функцію відправки welcome-email?» тут має 3 правильні відповіді, бо ні `service/user.py`, ні `service/notification.py`, ні нова `helpers/notify.py` не виглядають однозначно правильніше за інші. Це і є cost нечіткої структури — Claude вгадує, не знає.

## Стек

- Python 3.12–3.14
- FastAPI 0.110+ (async)
- SQLAlchemy 2.x з **asyncpg** (async driver)
- Alembic 1.13+ — одна revision, що створює всі 5 таблиць без BC-префіксу
- Postgres 18 у Docker
- `bcrypt` для паролів
- Pydantic v2 для request/response models

### Чому async?

FastAPI — async-first фреймворк. Async SQLAlchemy + asyncpg — найшвидший шлях до production-grade Python API. У stage-3 інверсія залежностей (Protocol vs concrete repo) природно лягає на `async def` методи.

### Чому Alembic?

Один інструмент і для stage-1, і для stage-2/3 — менше когнітивного навантаження для студента. У stage-1 — одна revision з усіма таблицями. У stage-2/3 — 5 окремих revisions з BC-prefix tables.

## Структура

```
stage-1-flat/
├── pyproject.toml
├── docker-compose.yml
├── Makefile
├── README.md
├── .env.example
├── alembic.ini
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/0001_init.py
├── scripts/smoke.sh
└── app/
    ├── main.py                 # FastAPI app
    ├── db.py                   # async engine + session
    ├── handler/                # HTTP layer (FastAPI routers)
    │   ├── user.py
    │   ├── product.py
    │   ├── order.py
    │   ├── subscription.py
    │   └── notification.py
    ├── service/                # business logic — все плоско
    │   ├── user.py
    │   ├── product.py
    │   ├── order.py
    │   ├── subscription.py
    │   └── notification.py
    ├── repository/             # DB access (raw SQL через AsyncSession)
    │   ├── user.py
    │   ├── product.py
    │   ├── order.py
    │   ├── subscription.py
    │   └── notification.py
    └── model/                  # entity dataclasses
        ├── user.py
        ├── product.py
        ├── order.py
        ├── subscription.py
        └── notification.py
```

## Швидкий старт

```bash
python3 -m venv .venv
source .venv/bin/activate     # Windows (Git Bash): source .venv/Scripts/activate
make doctor                   # перевірка: docker, python, активний venv, вільні порти
make install                  # залежності з requirements.lock.txt
make db-up                    # postgres у docker, з таймаутом очікування
make db-migrate               # міграції (db-up підтягнеться сам, якщо база не піднята)
make run                      # в ОКРЕМОМУ терміналі — процес не завершується
make smoke                    # 6 endpoints → all 2xx
make clean                    # зупинити базу і видалити том
```

Порт 5432 або 8080 зайнятий? Візьми інші — `make db-up PGPORT=5433`, `make run HTTP_PORT=8081`
(і тоді `make smoke BASE_URL=http://localhost:8081`). Постійний варіант — `cp .env.example .env`.

Щось не сходиться — [`TROUBLESHOOTING.md`](../../TROUBLESHOOTING.md).
## Ендпоінти

- `POST /auth/register` — реєстрація
- `POST /auth/login` — логін
- `GET  /products` — список продуктів
- `POST /orders` — створення замовлення
- `POST /subscriptions` — оформлення підписки (`basic`, `pro`, `enterprise`)
- `POST /notifications/test` — тестова нотифікація

## Чому ця структура — стартова, а не фінальна

`UserService` тут робить тільки `register` / `login`. Але як тільки треба «після реєстрації відправити welcome-email», ти стикаєшся з вибором:
- Викликати `NotificationService.send_test(...)` з `UserService.register(...)` напряму? Тоді UserService починає знати про Notifications
- Винести в новий `OnboardingService`? А де він живе — у `service/`? Тоді шар плутається з фічею
- Створити helper `helpers/send_welcome_email.py`? Тоді у `helpers/` лежить бізнес-логіка

Це не вирішується гарним кодом — це вирішується **Bounded Context**ами. Перехід у [`stage-2-feature-first`](../stage-2-feature-first) показує перший крок.
