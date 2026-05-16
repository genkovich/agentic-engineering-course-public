# Go stage-1-flat

**Layered (handler/service/repo) без Bounded Contexts.** BC існують тільки в голові команди — у файлах розкидані функції по шарах.

Це навмисно нечітка структура. Лекційний промпт «куди мені покласти функцію відправки welcome-email?» тут має 3 правильні відповіді, бо ні `service/user.go`, ні `service/notification.go`, ні нова `helpers/notify.go` не виглядають однозначно правильніше за інші. Це і є cost нечіткої структури — Claude вгадує, не знає.

## Стек

- Go 1.24
- chi/v5 для роутингу
- pgx/v5 для Postgres
- Postgres 18 у Docker
- bcrypt для паролів
- Без міграційного інструмента — `migrations/0001_init.sql` запускається через `psql`

## Структура

```
stage-1-flat/
├── main.go
├── go.mod
├── docker-compose.yml
├── migrations/
│   └── 0001_init.sql       # users, products, orders, subscriptions, notifications
├── Makefile
├── scripts/
│   └── smoke.sh
└── app/
    ├── handler/            # HTTP layer
    │   ├── user.go
    │   ├── product.go
    │   ├── order.go
    │   ├── subscription.go
    │   ├── notification.go
    │   └── json.go
    ├── service/            # business logic — все плоско
    │   ├── user.go
    │   ├── product.go
    │   ├── order.go
    │   ├── subscription.go
    │   └── notification.go
    ├── repository/         # DB access
    │   ├── user.go
    │   ├── product.go
    │   ├── order.go
    │   ├── subscription.go
    │   └── notification.go
    └── model/              # entity structs
        ├── user.go
        ├── product.go
        ├── order.go
        ├── subscription.go
        └── notification.go
```

## Швидкий старт

```bash
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

`UserService` тут робить тільки `Register` / `Login`. Але як тільки треба «після реєстрації відправити welcome-email», ти стикаєшся з вибором:
- Викликати `notificationService.SendTest(...)` з `userService.Register(...)` напряму? Тоді UserService починає знати про Notifications
- Винести в новий `OnboardingService`? А де він живе — у `service/`? Тоді шар плутається з фічею
- Створити helper `helpers/sendWelcomeEmail.go`? Тоді у `helpers/` лежить бізнес-логіка

Це не вирішується гарним кодом — це вирішується **Bounded Context**ами. Перехід у [`stage-2-feature-first`](../stage-2-feature-first) показує перший крок: 5 папок-контекстів і явні межі між ними.

## Сцена для скринкастів

Цей проект з'являється у скринкастах **1** і **3**:

- **Скринкаст 1:** `claude` у цій папці на промпт «куди покласти welcome-email» → 3 варіанти
- **Скринкаст 3:** `tree -L 2 app/` показує плоску шарувату структуру

Точні промпти і очікувані артефакти — у [`../screencast-prompts.md`](../screencast-prompts.md).
