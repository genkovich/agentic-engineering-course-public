# Staged migrations — course-lesson-mvp

These SQL files are **staged** artifacts produced by `sdlc-generate-data-model`.
`sdlc-implement-tasks` promotes them to the repo's live migrations tree,
re-stamping timestamps to avoid collisions with other in-flight features.

Conventions (per DB exception note in sdlc-final-state.md):
- Timestamp-prefixed filenames: `YYYYMMDDHHMMSS_<slug>.up.sql` / `.down.sql`
- Idempotent: `.up.sql` uses `IF NOT EXISTS`; `.down.sql` uses `DROP ... IF EXISTS`
- SQL-first (no ORM DSL)
- Only UNIQUE / NOT NULL / FK / indexes / `DEFAULT now()` for timestamps
- Audit columns: `created_at` only (immutable-first; no `updated_at` on event/audit tables)
- Hard delete — no soft-delete columns
- No CHECK constraints, no TRIGGER, no business DEFAULT values (DB as dumb storage)

Files in this directory:
- `20260523000001_add_is_methodist_to_org_members` — ALTER existing table
- `20260523000002_create_course_lesson_tables`     — 8 new tables
- `20260523000003_add_course_lesson_indexes`        — composite query indexes
