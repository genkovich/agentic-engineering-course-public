---
name: generate-data-model
description: >
  Use when the user wants to design the data model AND generate the actual
  forward + rollback migrations in one pass. Triggers on
  "data model for {slug}", "schema for {feature}", "generate migrations
  for {slug}", "DB design + migration", "stage 8+9 for {slug}",
  "/sdlc-generate-data-model {slug}". Default mode is greenfield-first:
  reads PRD §4 + SAD §6.4 ER + sequence diagrams + (optional) Go domain
  structs and produces docs/features/{slug}/data-model.md + migrations/*.up.sql
  + migrations/*.down.sql + a markdown report. Supersedes legacy
  design-db + plan-migration skills. Prerequisites:
  docs/features/{slug}/PRD.md (stage 03) + docs/features/{slug}/sad.md (stage 04) —
  hard refuse if missing.
---

# Skill: generate-data-model

End-to-end runner for the persistence cut: design + migrations + drift check. Greenfield-first by default; brownfield delta as `--mode brownfield`. Output is **shippable** — full `.up.sql` + `.down.sql` ready for `migrate up`, not a plan.

Supersedes the legacy `design-db` (stage 08 — data-model.md only) and `plan-migration` (stage 09 — migration plan only) skills. The DB-as-dumb-storage rules carry over verbatim. The opinionated additions are below ("Defaults" section).

## Owner

Backend Lead.

## When to use

- "data model for <slug>", "schema for <feature>", "generate migrations for <slug>".
- After PRD + SAD §6.4 (ER stub) + at least the critical sequences exist. Run after `complete-sequence-diagrams` so the skill knows every table the runtime needs.
- `/sdlc-generate-data-model <slug>` — explicit invocation.
- `/sdlc-generate-data-model <slug> --mode brownfield` — analyze existing `migrations/` and propose delta.
- `/sdlc-generate-data-model <slug> --drift-only` — just compare Go domain structs against current schema; no generation.
- Skip if `data-model.md` exists AND every entity in it has a corresponding pair of migration files.

## Inputs

- `<slug>` — same as for PRD / SAD.
- **Gate (hard refuse if missing):**
  - `docs/features/<slug>/PRD.md` — entities live in §4 user-story acceptance criteria.
  - `docs/features/<slug>/sad.md` — §6.4 ER section provides initial relationships.
  - Optional: `docs/features/<slug>/diagrams/` — sequences inform indexes (one index per query, justified).
  - Optional: `internal/modules/<...>/domain/*.go` (or stack-equivalent) — drift detection only.

## Defaults (the opinionated set)

These defaults are baked into the skill and into the baseline `.claude/rules/migrations.md` the skill writes on first run. They differ from common community defaults; the skill flags this explicitly in the report.

| Topic | Default | Why |
|---|---|---|
| Migration filename | `YYYYMMDDhhmmss_<slug>.up.sql` (timestamp) | Two parallel feature branches won't collide on `000034_`. |
| Idempotency in DDL | `CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO NOTHING` for seeds | Re-running a single migration on a partially-applied DB does not error. |
| Audit columns | `created_at TIMESTAMPTZ NOT NULL DEFAULT now()` only — **no `updated_at`** | Immutable-leaning: changes go through an audit table or event log if business needs them. |
| Delete strategy | Hard delete + audit table if business requires history | No `deleted_at`, no status-column for delete. DB stays simple; history is a separate concern. |
| PK | UUID v7, generated app-side | Cursor pagination, no insert sequence contention. |
| Naming | `plural snake_case` (`users`, `goal_progress`) | Postgres community standard. |
| Indexes | One per query (from sequences). Existing-table `CREATE INDEX CONCURRENTLY` always. | Each index has a write cost; `CONCURRENTLY` avoids long write locks. |
| Breaking changes | Auto-decompose to 3-step expand → backfill → contract | Zero-downtime by default. |
| New NOT NULL on existing table | Auto-decompose: add nullable → backfill → set NOT NULL | Default zero-downtime path. |
| String columns | `VARCHAR(N)` bounded; `TEXT` only for URLs / long descriptions | Schema-as-documentation; bounds drive validation. |
| JSONB | Only for semantically opaque payload (settings, metadata, polymorphic block.payload) | Structured fields → first-class columns. |
| Forbidden | `CHECK`, `TRIGGER`, `DEFAULT '<business value>'`, sequences-as-PK | "DB as dumb storage" — business logic lives in code. |
| Multi-DB (replica, sharding) | Out of scope | Single-DB only. |
| Partitioning, materialized views | Out of scope | Performance optimization, not contract. |

## Protocol

1. **Prereq check (hard).** `test -f docs/features/<slug>/PRD.md && test -f docs/features/<slug>/sad.md` → exit ≠ 0 = refuse with pointer to which prereq is missing.

2. **Rules bootstrap.** If `.claude/rules/migrations.md` is absent in the repo root, copy `./templates/rules-migrations-baseline.md` → `.claude/rules/migrations.md` and tell the user "I wrote a baseline rules file; edit it if your team disagrees with any default."

3. **Read prereqs in this order:**
   a. PRD §4 — extract entity candidates from acceptance criteria.
   b. SAD §6.4 — initial ER stub (often `<!-- TBD: relationships -->`).
   c. `docs/features/<slug>/diagrams/` — every sequence's `Note over API, DB: writes <table.column>` becomes a query requirement → index candidate.
   d. (Optional) `internal/modules/<...>/domain/*.go` — if present, the skill builds a struct-vs-DDL map for drift detection.
   e. (Brownfield only) `migrations/*.up.sql` — parse current schema offline (no live DB connection).

4. **Aggregate roots discussion.** Ask the user (or infer from PRD acceptance criteria): which aggregate roots? What lives around what? Lessons aggregate ContentBlocks; Tenant aggregates QuotaConfig. Without explicit aggregates the FK graph turns into a hairball.

5. **PK strategy.** UUID v7 by default. Confirm with the user only if PRD has explicit acceptance criteria that demand a different PK (e.g., lookup slug as PK).

6. **Column types and constraints.** For each entity:
   - `VARCHAR(N)` for bounded strings; choose N from PRD validation (`title: maxLength: 200` → `VARCHAR(200)`).
   - `TEXT` only for long descriptions / URLs.
   - `JSONB` only for opaque payloads (with a one-line justification in the data-model.md `Notes` column).
   - `TIMESTAMPTZ NOT NULL DEFAULT now()` for `created_at`. No `updated_at` (see Defaults).
   - `<!-- TBD -->` where honestly undecided.

7. **Indexes per query.** For each Mermaid sequence note `writes/reads <table.column>` produce an index candidate. Discard candidates that have no concrete query justification. Print a "Justification" column in `data-model.md`.

8. **Generate `docs/features/<slug>/data-model.md`** from the template (`./templates/data-model.md`):
   - ER Mermaid diagram (manual layout — not auto-generated; the skill writes a clean ordered block).
   - Entities table per aggregate.
   - Indexes table with `Query it serves` filled.

9. **Generate migration files** in `<repo-root>/migrations/` (or stack-specific folder if `.claude/rules/migrations.md` overrides):

   For each new entity:
   - **Greenfield** (default): one `<timestamp>_create_<entity>.up.sql` + `.down.sql` per entity (or per aggregate, if small).
   - **Brownfield** (`--mode brownfield`): diff vs parsed existing schema; produce ALTERs only.
   - `IF NOT EXISTS` on every `CREATE TABLE` / `CREATE INDEX`. `ON CONFLICT DO NOTHING` on every seed `INSERT`.
   - For existing-table `CREATE INDEX`: emit `CONCURRENTLY` AND warn that the file must contain only that one statement (golang-migrate transaction wrapper).
   - For new NOT NULL on existing table: emit 3 migration files (`add_nullable`, `backfill`, `set_not_null`); the user reviews the backfill SQL.

10. **Generate seeds.** Three buckets:
    - **Bootstrap** (admin user, default org) — first migration `<timestamp>_bootstrap_<thing>.up.sql`. Deterministic UUID v7 hardcoded (e.g., `00000000-0000-7000-8000-000000000001`).
    - **Lookup data** (statuses, currencies, rating scales) — separate migration `<timestamp>_seed_<table>.up.sql` with `INSERT ... ON CONFLICT DO NOTHING` (idempotent — re-runs are safe).
    - **Test fixtures** — NOT in `migrations/`. Generate Go factory functions in `internal/testfixtures/<entity>.go` (or stack-equivalent): `NewLesson(t *testing.T, db *sql.DB, opts ...Opt) *Lesson`. Document in `data-model.md` under "Test fixtures".
    - **PII guard:** the skill refuses to write a real-looking email / name / phone in any seed. Use `admin@example.test`, `user-<uuid>@example.test`, `Test User`. Hard rule.

11. **Drift detection (always runs; `--drift-only` short-circuits to here).** If Go domain structs exist:
    - For each struct field, look up the matching DB column.
    - Report mismatches in 4 categories: `field-without-column`, `column-without-field`, `type-mismatch`, `nullability-mismatch`.
    - **Auto-propose fix migrations** in the `_drift/` subfolder (user reviews before applying).

12. **Breaking changes — 3-step decomposition.** If the user describes a rename / drop / re-type:
    - Phase 1: add new column nullable + dual-write trigger from app side (not DB trigger).
    - Phase 2: backfill batched script (ETA + resumability — write a one-page `backfill-<column>.md` companion file).
    - Phase 3: drop old column. Each phase = separate migration file = separate PR = separate deploy.

13. **Self-check (the 4 mandatory checks, run as inline migration-checker logic).** For every generated file:
    - **Naming.** `plural snake_case`. Heading regex.
    - **down.sql reversibility.** Every CREATE has a matching DROP; every ADD COLUMN has a DROP COLUMN; every CREATE INDEX has a DROP INDEX.
    - **FK indexes.** Every `REFERENCES other_table(id)` has a `CREATE INDEX` on the FK column.
    - **Forbidden features.** Grep for `CHECK (`, `CREATE TRIGGER`, `DEFAULT '` followed by non-`now()` business literal. Fail with line numbers.

    Any failure → fix or surface to user (no silent commit).

14. **Generate report.** `docs/features/<slug>/_audit/data-model-<timestamp>.md`:
    - **Generated files:** list of all .up.sql / .down.sql / data-model.md.
    - **Default deviations applied:** which defaults differ from the user's repo conventions (e.g., "your repo uses sequential migration naming; I wrote timestamps — see Defaults table").
    - **Drift findings:** if any (with proposed fix migrations under `_drift/`).
    - **Breaking changes decomposed:** if any 3-step sequence was generated.
    - **TBDs:** every `<!-- TBD -->` in data-model.md with file:line.
    - **Next stage:** `define-api <slug>` (stage 10).

15. **Propose commit.** `08+09: data-model + migrations for <slug>` + next owner (Backend Lead → stage 10 API contracts via `define-api`).

## Questions for discussion

- Aggregate roots — what owns what?
- Where does the user explicitly want `updated_at` (overriding the immutable-first default)? Surfacing this is mandatory; the skill never adds `updated_at` silently.
- Soft-delete or hard-delete + audit? Hard-delete is the default; the skill needs explicit override.
- Indexes — any "just in case" that the user wants despite no concrete query?
- JSONB usage — confirm each candidate column.
- For breaking changes — does the user accept 3-step decomposition or do they have a maintenance window?

## Definition of Done

- `data-model.md` exists with ER, every entity, every index with query justification.
- For every entity / change, a matched pair of `.up.sql` + `.down.sql` exists.
- All 4 self-checks pass (naming, down reversibility, FK indexes, forbidden features).
- Audit report in `_audit/data-model-<timestamp>.md`.
- Drift report (if drift detected) with `_drift/*.sql` proposals.

## Anti-patterns

- **Business defaults in DB** (`DEFAULT 'pending'`). Only `DEFAULT now()` for timestamps; the rest in app code.
- **CHECK constraints on business invariants.** Business logic lives in code.
- **Index "just in case" without a concrete query.** Each index costs write performance.
- **TEXT for everything.** Bounded strings → `VARCHAR(N)`.
- **Triggers / stored procedures.** DB stays dumb.
- **PK from DB sequence.** Default UUID v7 from app — no blocking on insert sequence.
- **One mega-migration with 5 ALTERs.** Rollback becomes all-or-nothing. Split.
- **DROP COLUMN before deploying new code.** Breaks running pods between phases. Always 3-step decomposition.
- **Real-looking PII in seeds** (Gmail / .ua emails). Use `example.test`.
- **Sequential migration filenames in multi-developer repos.** Two parallel feature branches collide on `000034_`. Use timestamps.
- **Live DB introspection without offline parse fallback.** CI does not have DB credentials; parse the SQL files.
- **Generating a baseline `rules/migrations.md` and forgetting to tell the user.** The skill MUST report when it bootstraps a rules file.

## Templates

→ [./templates/data-model.md](./templates/data-model.md) — output structure for the design doc.
→ [./templates/rules-migrations-baseline.md](./templates/rules-migrations-baseline.md) — baseline `.claude/rules/migrations.md` copied at step 2 when missing.
→ [sdlc/document-templates/migration-plan.md](../../../document-templates/migration-plan.md) — cross-feature; folded into the audit report, not generated as a separate file in greenfield.

## Example invocation

> **User:** "data model for course-lesson-mvp"
>
> **Skill behavior:**
> 1. `test -f docs/features/course-lesson-mvp/PRD.md && test -f docs/features/course-lesson-mvp/sad.md` → OK.
> 2. `.claude/rules/migrations.md` missing → bootstrapped from baseline. Reported to user.
> 3. Reads PRD (entities: Lesson, ContentBlock, MediaBlob, AuditEvent), SAD §6.4 (ER stub: Lesson ||--o{ ContentBlock), sequences (5 files in diagrams/ — index on `lessons.course_id` for listLessons; on `content_blocks.lesson_id` for getLesson with blocks).
> 4. Aggregate roots: Lesson aggregates ContentBlock; MediaBlob is referenced (signed URL in block.payload).
> 5. PK: UUID v7 app-side.
> 6. Types: `title VARCHAR(200)` (from PRD AC `maxLength: 200`), `slug VARCHAR(120) UNIQUE(course_id, slug)`, `status VARCHAR(32)` (enum-in-app), `block.payload JSONB` (polymorphic — ADR-0001), `published_at TIMESTAMPTZ NULL`, all `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`. No `updated_at`.
> 7. Indexes: `idx_lessons_course_id` (listLessons), `idx_blocks_lesson_id` (getLesson), `idx_lessons_published_per_course WHERE status='published'` (partial — listPublishedLessons from sequence US-4).
> 8. Writes `docs/features/course-lesson-mvp/data-model.md` (ER + 3 entity tables + indexes table).
> 9. Writes 4 migration pairs in `beer-lms-api/migrations/`: `20260523120000_create_lessons.up.sql/.down.sql`, `20260523120001_create_content_blocks.up.sql/.down.sql`, `20260523120002_create_media_blobs.up.sql/.down.sql`, `20260523120003_create_audit_events.up.sql/.down.sql`. All `IF NOT EXISTS`.
> 10. Seeds: none required (no admin / lookup tables in this feature). Test fixtures: writes `beer-lms-api/internal/testfixtures/lesson.go` with `NewLesson`, `NewContentBlock` factories. PII guard satisfied.
> 11. Drift detect: Go structs not yet written → skipped (no drift to report).
> 12. Self-check: all 4 pass. naming OK, down.sql reverses every up, FK indexes present (`idx_blocks_lesson_id`), no forbidden features.
> 13. Audit report `_audit/data-model-2026-05-23.md`: lists generated files, flags "timestamp naming differs from repo's existing sequential `000003_seed_admin.up.sql` — see Defaults table"; lists no drift; lists no breaking changes; lists 1 TBD (the user marked `block.payload` schema as `<!-- TBD: lock with ADR-0001 -->`); next stage: `define-api course-lesson-mvp`.
> 14. Commit suggestion: `08+09: data-model + migrations for course-lesson-mvp`.
