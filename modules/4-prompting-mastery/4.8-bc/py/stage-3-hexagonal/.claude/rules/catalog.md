---
name: catalog-bc-rules
description: Rules for the Catalog Bounded Context (Python)
paths:
  - "app/catalog/**"
---

# Catalog BC

Scope: products, categories. Read-only at this stage, no published events.

## Structure

```
app/catalog/
├── domain/
│   ├── product.py          # Product dataclass
│   └── repository.py       # Repository Protocol
├── app/service.py          # List use case
├── infra/
│   ├── postgres/product_repo.py
│   └── http/handler.py     # GET /products
└── module.py
```

## Rules

- Domain does not import other BCs
- Read-only for now — adding Create/Update/Delete needs an admin scope
  from Auth (then we decide: ACL or direct event-listener)
- `Product.price_cents: int` — money is always cents

## Anti-patterns

- ❌ Discount / coupon business logic in `app/catalog/domain/`. That is Commerce BC
- ❌ Admin authorization in `app/catalog/infra/http/handler.py`. Should be a
  middleware from a shared auth helper (added when admin endpoints land)
