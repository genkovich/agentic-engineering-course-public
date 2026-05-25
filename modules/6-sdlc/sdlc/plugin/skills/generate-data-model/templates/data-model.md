---
status: Draft
owner: "<Backend Lead name>"
reviewers: []
updated_at: "<YYYY-MM-DD>"
feature_size: S
stage: "08"
ticket: "<ticket-id>"
---

# Data model — <feature>

<!-- Stage 08 → see SDLC/plugin/skills/design-db/SKILL.md -->

## ER diagram

```mermaid
erDiagram
    USER ||--o{ <ENTITY> : has
    <ENTITY> {
        uuid id PK
        varchar(255) name
        timestamp created_at
    }
```

## Entities

### `<entity>`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK, generated app-side (UUID v7) | <...> |
| `<col>` | VARCHAR(N) | NOT NULL | <...> |
| `created_at` | TIMESTAMPTZ | NOT NULL DEFAULT now() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL DEFAULT now() | |

**Access patterns:**
- <pattern 1> → index `<idx_name>` on `<columns>`.
- <pattern 2> → <...>.

**Constraints:** UNIQUE on `<...>`, FK → `<other_table>(id)`.

<!-- Why: business logic lives in code, not in DB. Only UNIQUE / NOT NULL / FK / DEFAULT now() / indexes. -->

## Indexes

| Index | Columns | Query it serves |
|---|---|---|
| <idx_1> | <cols> | <query> |
