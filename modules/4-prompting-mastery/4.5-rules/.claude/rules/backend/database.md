---
paths:
  - "**/migrations/**"
  - "**/models/**"
---

# Database rules

Завантажується для усього під будь-якою `migrations/` або `models/` директорією. Migrations - SQL, models - Go structs з тегами.

## Migrations

- Use `golang-migrate`. File naming: `NNN_description.up.sql` plus `NNN_description.down.sql`. Numbers are sequential, no gaps.
- Every `up.sql` has a matching `down.sql` that fully reverses the change. Test the down path locally before merging.
- One logical change per migration. Adding a column and creating an index are separate migrations.
- Never edit a migration after it has run on any environment. Add a new migration that fixes the previous one.

## Schema constraints

- Database stores data, not business defaults. No `DEFAULT 'active'` on a status column - the application sets initial values.
- No `CHECK` constraints for business rules. Validation lives in code where it can return useful error messages.
- No triggers. They hide behavior from the application layer and break replay.
- Allowed: `UNIQUE`, `NOT NULL`, foreign keys, indexes, `DEFAULT now()` for `created_at` and `updated_at`.

## Identifiers and types

- Primary keys are `uuid` columns. UUID v7 generated in the application layer, never `gen_random_uuid()` or sequence-based IDs.
- Bounded text uses `VARCHAR(N)` with explicit length. `TEXT` is reserved for descriptions, URLs, freeform content.
- Timestamps are `timestamptz`. Application stores UTC, presentation layer converts.
- Money stored as `numeric(20, 4)`. Never `float`, never `int` cents without a comment explaining the unit.

## Indexes

- Foreign keys always have a covering index. Postgres does not create one automatically.
- Add indexes when a query plan shows a sequential scan on a hot path. Do not add indexes preemptively.
- Composite index column order: equality columns first, then range columns, then sort columns.
