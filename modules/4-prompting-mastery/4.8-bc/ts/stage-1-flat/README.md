# TS stage-1-flat

**Layered (handler/service/repository/model) без Bounded Contexts.** BC існують тільки в голові команди — у файлах розкидані функції по шарах.

Це навмисно нечітка структура. Лекційний промпт «куди мені покласти функцію відправки welcome-email?» тут має 3 правильні відповіді, бо ні `service/user.ts`, ні `service/notification.ts`, ні нова `helpers/notify.ts` не виглядають однозначно правильніше за інші. Це і є cost нечіткої структури — Claude вгадує, не знає.

## Стек

- Node.js 22+
- Fastify 4 — HTTP сервер
- pg — Postgres драйвер (raw SQL)
- bcryptjs — паролі
- TypeScript 5 + tsx (dev runtime)
- Postgres 18 у Docker
- Без міграційного інструмента — `migrations/0001_init.sql` запускається через `psql`

## Структура

```
stage-1-flat/
├── package.json
├── tsconfig.json
├── docker-compose.yml
├── migrations/
│   └── 0001_init.sql       # users, products, orders, subscriptions, notifications
├── Makefile
├── scripts/
│   └── smoke.sh
└── src/
    ├── index.ts            # Fastify bootstrap
    ├── db.ts               # postgres pool
    ├── handler/            # HTTP layer
    │   ├── user.ts
    │   ├── product.ts
    │   ├── order.ts
    │   ├── subscription.ts
    │   └── notification.ts
    ├── service/            # business logic — все плоско
    │   ├── user.ts
    │   ├── product.ts
    │   ├── order.ts
    │   ├── subscription.ts
    │   └── notification.ts
    ├── repository/         # DB access
    │   ├── user.ts
    │   ├── product.ts
    │   ├── order.ts
    │   ├── subscription.ts
    │   └── notification.ts
    └── model/              # entity types
        ├── user.ts
        ├── product.ts
        ├── order.ts
        ├── subscription.ts
        └── notification.ts
```

## Швидкий старт

```bash
npm install
make db-up
make db-migrate
make run                  # в окремому терміналі
make smoke                # 6 endpoints → all 2xx
```

Після завершення:
```bash
make clean
```

## Ендпоінти

- `POST /auth/register` — реєстрація користувача
- `POST /auth/login` — логін
- `GET  /products` — список продуктів
- `POST /orders` — створення замовлення
- `POST /subscriptions` — оформлення підписки
- `POST /notifications/test` — тестова нотифікація

## Чому ця структура — стартова, а не фінальна

`UserService` тут робить тільки `register` / `login`. Але як тільки треба «після реєстрації відправити welcome-email», ти стикаєшся з вибором:
- Викликати `notificationService.sendTest(...)` з `userService.register(...)` напряму? Тоді UserService починає знати про Notifications
- Винести в новий `OnboardingService`? А де він живе — у `service/`? Тоді шар плутається з фічею
- Створити helper `helpers/sendWelcomeEmail.ts`? Тоді у `helpers/` лежить бізнес-логіка

Це не вирішується гарним кодом — це вирішується **Bounded Context**ами. Перехід у [`stage-2-feature-first`](../stage-2-feature-first) показує перший крок: 5 папок-контекстів і явні межі між ними.
