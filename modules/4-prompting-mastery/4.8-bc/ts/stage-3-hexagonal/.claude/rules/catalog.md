---
name: catalog-bc-rules
description: Rules для Catalog Bounded Context
paths:
  - "src/catalog/**"
---

# Catalog BC

Scope: продукти, категорії. На цьому етапі read-only, без published events.

## Структура

```
src/catalog/
├── domain/
│   ├── product.ts          # Product entity
│   └── repository.ts       # Repository interface
├── app/service.ts          # list use case
├── infra/
│   ├── postgres/productRepo.ts
│   └── http/handler.ts     # GET /products
└── module.ts
```

## Правила

- Domain не імпортує інших BC
- Поки що read-only — додавання Create/Update/Delete потребує admin scope з Auth (тоді вирішуємо: ACL чи прямий event-listener)
- `Product.priceCents: number` — гроші завжди cents (через `BIGINT` у БД, парситься з string у repo)

## Anti-patterns

- ❌ Бізнес-логіка про знижки, купони у `src/catalog/domain/`. Це Commerce BC
- ❌ Admin authorization у `src/catalog/infra/http/handler.ts`. Має бути middleware з shared/auth (поки не існує — додавай разом з admin endpoints)
