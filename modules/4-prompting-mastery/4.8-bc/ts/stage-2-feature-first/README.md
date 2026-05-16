# TS stage-2-feature-first

**Vertical Slice — кожен BC у власній папці.** Це другий рівень зрілості зі Slide 7. Підходить для більшості реальних сервісів.

На відміну від `stage-1-flat`, де `handler/service/repository/model` живуть плоско, тут код кожної фічі лежить разом. Claude знає, де шукати: `src/features/notifications/` — все про нотифікації, `src/features/auth/` — все про авторизацію.

На відміну від `stage-3-hexagonal`, тут немає `domain/app/infra` всередині кожного BC і немає arch-test. Це проміжний рівень: чіткі межі між фічами, але внутрішня структура кожного BC проста.

## Стек

- Node.js 22+
- Fastify 4 — HTTP сервер
- pg — Postgres драйвер (raw SQL)
- bcryptjs — паролі
- TypeScript 5 + tsx
- Postgres 18 у Docker

## Структура

```
stage-2-feature-first/
├── package.json
├── tsconfig.json
├── docker-compose.yml
├── Makefile
├── README.md
├── .env.example
├── migrations/                  # один SQL на BC
│   ├── 0001_auth.sql
│   ├── 0002_catalog.sql
│   ├── 0003_commerce.sql
│   ├── 0004_billing.sql
│   └── 0005_notifications.sql
├── scripts/smoke.sh
└── src/
    ├── index.ts                 # імпортує BC, реєструє маршрути
    ├── shared/
    │   ├── db.ts                # postgres pool
    │   ├── apperr.ts            # типізовані помилки
    │   └── httputil.ts          # error mapping
    └── features/
        ├── auth/                # ⬇ vertical slice — handler+service+repo+model разом
        │   ├── handler.ts
        │   ├── service.ts
        │   ├── repository.ts
        │   ├── model.ts
        │   └── index.ts
        ├── catalog/             # similar
        ├── commerce/            # similar
        ├── billing/             # similar
        └── notifications/       # similar
```

## Швидкий старт

```bash
npm install
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

Уяви промпт «куди мені покласти функцію перевірки купона». У stage-1 Claude вгадає (`service/order.ts`? `service/billing.ts`? `helpers/coupon.ts`?). Тут — однозначно: `features/commerce/` (купон — частина оформлення замовлення) або `features/billing/` (якщо купон стосується підписок).

`tree -L 1 src/features/` показує вертикальну структуру:
```
src/features/
├── auth/
├── catalog/
├── commerce/
├── billing/
└── notifications/
```

5 BC = 5 папок. Це матеріалізована карта системи у файлах.

## Що НЕ покращується vs stage-1

- Cross-BC імпорти все ще можливі. Якщо Auth після реєстрації захоче відправити email — він напряму імпортуватиме `notifications.Service` і викличе. Це працює, але створює tight coupling, що не ловиться компілятором
- Domain типи змішані з infra типами. `auth.User` живе у `model.ts`, але в тій самій папці, що й `repository.ts` з SQL-запитами. Якщо завтра треба замінити Postgres на Redis — треба міняти логіку у `service.ts`, бо `User` має поля під SQL-схему
- `shared/` може поступово розростатись. Без жорсткого правила «що туди можна» — за рік стане смітником

Stage-3-hexagonal вирішує обидва ці питання через `domain/app/infra` split + interface inversion + `dependency-cruiser`.
