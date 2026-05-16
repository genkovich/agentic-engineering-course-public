# Go stage-2-feature-first

**Vertical Slice — кожен BC у власній папці.** Це другий рівень зрілості зі Slide 7. Підходить для більшості реальних сервісів.

На відміну від `stage-1-flat`, де `handler/service/repository/model` живуть плоско, тут код кожної фічі лежить разом. Claude знає, де шукати: `app/notifications/` — все про нотифікації, `app/auth/` — все про авторизацію.

На відміну від `stage-3-hexagonal`, тут немає `domain/app/infra` всередині кожного BC і немає arch-test. Це проміжний рівень: чіткі межі між фічами, але внутрішня структура кожного BC проста.

## Стек

- Go 1.24
- chi/v5 — роутинг
- pgx/v5 — Postgres
- Postgres 18 у Docker
- bcrypt — паролі

## Структура

```
stage-2-feature-first/
├── main.go
├── go.mod
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
├── shared/
│   ├── db/db.go                 # postgres pool
│   ├── apperr/apperr.go         # типізовані помилки
│   └── httputil/json.go
└── app/
    ├── auth/                    # ⬇ vertical slice — handler+service+repo+model разом
    │   ├── handler.go
    │   ├── service.go
    │   ├── repository.go
    │   └── model.go
    ├── catalog/
    │   ├── handler.go
    │   ├── service.go
    │   ├── repository.go
    │   └── model.go
    ├── commerce/                # similar
    ├── billing/                 # similar
    └── notifications/           # similar
```

## Швидкий старт

```bash
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

Уяви промпт «куди мені покласти функцію перевірки купона». У stage-1 Claude вгадає (`service/order.go`? `service/billing.go`? `helpers/coupon.go`?). Тут — однозначно: `app/commerce/` (купон — частина оформлення замовлення) або `app/billing/` (якщо купон стосується підписок).

`tree -L 1 app/` показує вертикальну структуру:
```
app/
├── auth/
├── catalog/
├── commerce/
├── billing/
└── notifications/
```

5 BC = 5 папок. Це матеріалізована карта системи у файлах.

## Що НЕ покращується vs stage-1

- Cross-BC імпорти все ще можливі. Якщо Auth після реєстрації захоче відправити email — він напряму імпортуватиме `notifications.Service` і викличе. Це працює, але створює tight coupling, що не ловиться компілятором
- Domain типи змішані з infra типами. `auth.User` живе у `model.go`, але в тому ж пакеті, що й `repository.go` з pgx-кодом. Якщо завтра треба замінити Postgres на Redis — треба міняти логіку у `service.go`, бо `User` має поля під SQL-схему
- `shared/` може поступово розростатись. Без жорсткого правила «що туди можна» — за рік стане смітником

Stage-3-hexagonal вирішує обидва ці питання через `domain/app/infra` split + interface inversion + `make arch-test`.

## Сцена для скринкастів

Цей проект з'являється у скринкастах **2** і **3**:

- **Скринкаст 2:** Excalidraw з 12 пост-ітами → `tree -L 1 app/` → 5 папок-контекстів
- **Скринкаст 3:** `tree -L 2 app/notifications/` показує проміжну зрілість — все в одному пакеті, але вже відокремлене від інших BC

Точні промпти і очікувані артефакти — у [`../screencast-prompts.md`](../screencast-prompts.md).
