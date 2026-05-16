# Python stage-2-feature-first

**Vertical Slice — кожен BC у власній папці.** Це другий рівень зрілості зі Slide 7. Підходить для більшості реальних сервісів.

На відміну від `stage-1-flat`, де `handler/service/repository/model` живуть плоско, тут код кожної фічі лежить разом. Claude знає, де шукати: `app/features/notifications/` — все про нотифікації, `app/features/auth/` — все про авторизацію.

На відміну від `stage-3-hexagonal`, тут немає `domain/app/infra` всередині кожного BC і немає arch-test. Це проміжний рівень: чіткі межі між фічами, але внутрішня структура кожного BC проста.

## Стек

- Python 3.12
- FastAPI 0.110+ (async)
- SQLAlchemy 2.x з **asyncpg** (async driver)
- Alembic 1.13+ — 5 окремих revisions, по одній на BC, з префіксом таблиць
- Postgres 18 у Docker
- `passlib[bcrypt]` — паролі
- Pydantic v2 — request/response

## Структура

```
stage-2-feature-first/
├── pyproject.toml
├── docker-compose.yml
├── Makefile
├── README.md
├── .env.example
├── alembic.ini
├── migrations/                  # одна revision на BC
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_auth.py             # auth_users
│       ├── 0002_catalog.py          # catalog_categories, catalog_products
│       ├── 0003_commerce.py         # commerce_orders
│       ├── 0004_billing.py          # billing_subscriptions
│       └── 0005_notifications.py    # notifications_messages
├── scripts/smoke.sh
└── app/
    ├── main.py
    ├── shared/
    │   ├── db.py                # async engine + session
    │   ├── apperr.py            # типізовані AppError
    │   └── httputil.py          # error mapping
    └── features/
        ├── auth/                # ⬇ vertical slice — handler+service+repository+model разом
        │   ├── __init__.py
        │   ├── handler.py
        │   ├── service.py
        │   ├── repository.py
        │   └── model.py
        ├── catalog/             # similar
        ├── commerce/            # similar
        ├── billing/             # similar
        └── notifications/       # similar
```

## Швидкий старт

```bash
pip install -e .
make db-up
make db-migrate
make run                  # окремий термінал
make smoke                # 6 endpoints → all 2xx
```

## Ендпоінти

- `POST /auth/register`, `POST /auth/login` — Auth feature
- `GET  /products` — Catalog feature
- `POST /orders` — Commerce feature
- `POST /subscriptions` — Billing feature
- `POST /notifications/test` — Notifications feature

## Що `feature-first` дає Claude

`tree -L 1 app/features/` показує вертикальну структуру:
```
app/features/
├── auth/
├── catalog/
├── commerce/
├── billing/
└── notifications/
```

5 BC = 5 папок. Це матеріалізована карта системи у файлах.

## Що НЕ покращується vs stage-1

- Cross-BC імпорти все ще можливі. Якщо Auth після реєстрації захоче відправити email — він напряму імпортуватиме `notifications.service.Service` і викличе. Це працює, але створює tight coupling, що не ловиться компілятором / лінтером
- Domain типи змішані з infra типами. `auth.User` живе в `model.py`, але в тому ж пакеті, що й `repository.py` з SQLAlchemy кодом. Якщо завтра треба замінити Postgres на Redis — треба міняти логіку у `service.py`, бо `User` має поля під SQL-схему
- `shared/` може поступово розростатись. Без жорсткого правила — за рік стане смітником

Stage-3-hexagonal вирішує обидва ці питання через `domain/app/infra` split + Protocol-based inversion + `make arch-test` з `import-linter`.
