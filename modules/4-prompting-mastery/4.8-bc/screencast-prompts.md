# Промпти зі скринкастів — лекція 4.8 Bounded Contexts

Точні промпти, які використовуються у кожному з 6 скринкастів. Скопіюй відповідний блок у Claude Code і відтвориш матеріал.

---

## Скринкаст 1 — той самий промпт, дві різні структури

**Контраст:** одне й те саме питання на flat і на hexagonal. У першому випадку Claude вгадує (3 варіанти), у другому дає однозначну відповідь.

### Запуск 1: stage-1-flat

```bash
cd 4.8-bc/go/stage-1-flat
claude
```

### Промпт

```
Куди мені покласти функцію відправки welcome-email новим користувачам?
```

### Очікуваний артефакт (stage-1-flat)

Claude вгадує — пропонує один з варіантів без впевненості:
- `app/service/user.go`
- `app/service/email.go`
- `app/helpers/notify.go`

Структура `handler/service/repo` плоска, BC не виражений → відповідь не однозначна.

### Запуск 2: stage-3-hexagonal

```bash
cd 4.8-bc/go/stage-3-hexagonal
claude
```

Той самий промпт.

### Очікуваний артефакт (stage-3-hexagonal)

Одна однозначна відповідь:
- Файл: `notifications/app/service.go`
- Subscriber на `auth.UserRegistered` у `notifications/infra/events/subscriber.go`
- Шлях прописаний у `CLAUDE.md` і захищений `make arch-test`

---

## Скринкаст 2 — Event Storming lite → папки

**Контраст:** 12 пост-ітів у 5 кольорових рамках з Excalidraw → 5 папок у `app/`.

### Excalidraw

12 пост-ітів з подіями:
```
UserRegistered, EmailVerified              → Auth (помаранчевий)
ProductViewed, WishlistAdded               → Catalog (зелений)
CartCreated, OrderPlaced,
PaymentFailed, PaymentSuccess              → Commerce (синій)
OrderShipped, DeliveryConfirmed            → Fulfillment (жовтий)
EmailSent, PushSent                        → Notifications (рожевий)
```

### Перехід до коду

```bash
cd 4.8-bc/go/stage-2-feature-first
tree -L 1 app/
```

### Очікуваний артефакт

```
app/
├── auth/
├── catalog/
├── commerce/
├── billing/
└── notifications/
```

Та сама пʼятірка контекстів зі стікерів — тепер як пʼять папок.

---

## Скринкаст 3 — три плани папок паралельно

**Контраст:** 3 термінали в 3 папках monorepo показують одну й ту саму фічу `notifications` на 3 рівнях зрілості.

### Термінал 1: stage-1-flat

```bash
cd 4.8-bc/go/stage-1-flat
tree -L 2 app/
```

Очікуваний артефакт:
```
app/
├── handler/
│   ├── user.go
│   └── notification.go
├── service/
│   ├── user.go
│   └── notification.go
└── repository/
    ├── user.go
    └── notification.go
```

`notifications` не існує як одиниця — лише функції, розкидані по шарах.

### Термінал 2: stage-2-feature-first

```bash
cd 4.8-bc/go/stage-2-feature-first
tree -L 2 app/notifications/
```

Очікуваний артефакт:
```
app/notifications/
├── handler.go
├── service.go
├── repository.go
└── model.go
```

Окрема папка — увесь код фічі разом.

### Термінал 3: stage-3-hexagonal

```bash
cd 4.8-bc/go/stage-3-hexagonal
tree -L 3 notifications/
```

Очікуваний артефакт:
```
notifications/
├── domain/
│   ├── notification.go
│   └── repository.go
├── app/
│   └── service.go
└── infra/
    ├── postgres/
    │   └── repo.go
    └── http/
        ├── handler.go
        ├── routes.go
        └── dto.go
```

---

## Скринкаст 4 — arch-test ловить порушення (Go / TS / Py)

**Контраст:** одне й те саме порушення меж — три різних інструмента, єдиний результат: CI fails.

### Go: go-arch-lint

```bash
cd 4.8-bc/go/stage-3-hexagonal
make install     # один раз: залежності + прогрів лінтера
```

Відкрий `notifications/domain/notification.go` і додай навмисне порушення — імпорт з чужого BC і з infra-шару. **Важливо:** порушення має компілюватися, інакше замість архітектурної помилки отримаєш банальне `imported and not used` від компілятора, і скринкаст показуватиме не те. Тому імпорт одразу використовується:

```go
import (
	"github.com/google/uuid"

	billingpg "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/infra/postgres"
)

// НАВМИСНЕ порушення для демонстрації arch-test.
var _ = billingpg.NewSubscriptionRepo
```

Спочатку покажи, що код валідний, і лише тоді запусти арх-тест:

```bash
go build ./...        # компілюється
make arch-test; echo $?
```

Реальний вивід:
```
go-arch-lint v1.17.0
module: github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal
linters:
   On | Base: component imports # always on
   On | Advanced: vendor imports
  Off | Advanced: method calls and dependency injections

Component notifications-domain shouldn't depend on
github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/infra/postgres
in .../notifications/domain/notification.go:11

--
total notices: 1

✗ go-arch-lint знайшов порушення меж (список вище).
make: *** [arch-test] Error 2
2
```

Код виходу ненульовий — саме це і зупиняє CI. (`2` віддає make; сам `scripts/arch-test.sh`, який ганяє CI, віддає `1`.)

Виправ через інверсію:
1. Створи `notifications/domain/payment_status.go` з `interface PaymentStatusReader`
2. Реалізацію залиш у `billing/infra` (там вона і має бути, бо це адаптер до постгресу білінгу)
3. Інжекти interface через DI у `notifications/app/service.go`
4. Запусти `make arch-test` знову → `✓ No violations found`

**Побічний кадр, який варто зняти:** зелений арх-тест сам по собі нічого не доводить — рівно так само виглядав зламаний лінтер, який взагалі не аналізував код. Тому поруч є негативний контроль:

```bash
make arch-test-selftest
# Негативний контроль: лінтер має знайти навмисне порушення a → b
# ✓ Лінтер коректно ловить порушення.
```

### TS: dependency-cruiser

```bash
cd 4.8-bc/ts/stage-3-hexagonal
make install
```

Те саме порушення у `src/notifications/domain/notification.ts`:

```ts
import { PgSubscriptionRepo } from "../../billing/infra/postgres/subscriptionRepo.js";
export type BillingRepoAlias = PgSubscriptionRepo;
```

```bash
make arch-test
```

Реальний вивід:
```
  error no-cross-context: src/notifications/domain/notification.ts → src/billing/infra/postgres/subscriptionRepo.ts
  error domain-no-infra: src/notifications/domain/notification.ts → src/billing/infra/postgres/subscriptionRepo.ts

x 2 dependency violations (2 errors, 0 warnings). 43 modules, 95 dependencies cruised.
```

Одне порушення ловиться двома правилами одразу: і як cross-BC імпорт, і як domain → infra.

### Python: import-linter

```bash
cd 4.8-bc/py/stage-3-hexagonal
source .venv/bin/activate && make install
```

Те саме порушення у `app/notifications/domain/notification.py`:

```python
from app.billing.infra.postgres.subscription_repo import PgSubscriptionRepo  # noqa: F401
```

```bash
make arch-test
```

Реальний вивід:
```
Contracts: 5 kept, 1 broken.

----------------
Broken contracts
----------------

BCs are independent
-------------------

app.notifications is not allowed to import app.billing:

- app.notifications.domain.notification -> app.billing.infra.postgres.subscription_repo (l.2)
```

**Висновок:** інструмент різний (`go-arch-lint`, `dependency-cruiser`, `import-linter`), формати повідомлень відрізняються — правило одне і ловиться автоматично у CI.

---

## Скринкаст 5 — AI кладе код у правильне BC (кульмінація)

**Контраст:** Claude генерує endpoint, і файл потрапляє у правильний BC автоматично — без явних інструкцій про шлях.

### Запуск

```bash
cd 4.8-bc/go/stage-3-hexagonal
claude
```

### Промпт

```
Додай endpoint POST /notifications/test, що приймає userID
і шле тестовий email через існуючий Sender.
```

### Очікуваний артефакт

Claude автоматично:
- Створює `notifications/infra/http/handler.go` (НЕ `main.go`, НЕ `shared/`)
- Реюзає `notifications/app/service.go` — не дублює логіку
- НЕ імпортує з `auth/` чи `billing/` напряму
- Реєструє route у `notifications/infra/http/routes.go` через registrar pattern
- Запускає `make arch-test` після генерації → `✓ No violations found`

Це і є кульмінація лекції. CLAUDE.md з BC-правилами + arch-test = поведінка Claude передбачувана.

---

## Скринкаст 6 — BC Map як живий документ

**Контраст:** ARCHITECTURE.md з mermaid рендериться однаково в Obsidian і в GitHub PR preview. Додавання нового BC = додавання ноди + 2 стрілок у mermaid.

### Запуск

```bash
cd 4.8-bc/go/stage-3-hexagonal
cursor ARCHITECTURE.md
```

(або `code` / `vim` / `obsidian://...`)

### Дія

Покажи рендер mermaid BC Map в Obsidian (плагін `mermaid-tools`) — графічна діаграма пʼяти контекстів зі стрілками подій. Покажи той самий файл у preview на GitHub — браузер рендерить mermaid нативно.

Тепер додай новий BC `reviews` (відгуки на товари):
1. Створи папки `reviews/{domain,app,infra}` з порожніми entity і service
2. Онови `ARCHITECTURE.md` — додай рядок у секцію BC list і ноду в mermaid-граф
3. Додай дві стрілки подій: `Catalog → Reviews` (`ProductPurchased`) і `Reviews → Notifications` (`ReviewPosted`)

### Очікуваний артефакт у `ARCHITECTURE.md`

```mermaid
graph LR
    Auth["Auth"]
    Catalog["Catalog"]
    Reviews["Reviews"]
    Notifications["Notifications"]

    Catalog -->|ProductPurchased event| Reviews
    Reviews -->|ReviewPosted event| Notifications
```

Збережи файл, перезавантаж preview в Obsidian — граф перемальовується автоматично.

**Висновок:** BC Map — не одноразова PowerPoint-діаграма. Це жива секція в `ARCHITECTURE.md`, що оновлюється з кожним новим контекстом.
