---
name: catalog-bc-rules
description: Rules для Catalog Bounded Context
paths:
  - "catalog/**"
---

# Catalog BC

Scope: продукти, категорії. На цьому етапі read-only, без published events.

## Структура

```
catalog/
├── domain/product.go     # Product, Category, Repository interface
├── app/service.go        # List use case
├── infra/
│   ├── postgres/repo.go
│   └── http/handler.go   # GET /products
└── module.go
```

## Правила

- Domain не імпортує інших BC
- Поки що read-only — додавання Create/Update/Delete потребує admin scope з Auth (тоді вирішуємо: ACL чи прямий event-listener)
- `Product.PriceCents int64` — гроші завжди cents

## Anti-patterns

- ❌ Бізнес-логіка про знижки, купони у `catalog/domain/`. Це Commerce BC
- ❌ Admin authorization у `catalog/infra/http/handler.go`. Має бути middleware з shared/auth (поки не існує — додавай разом з admin endpoints)
