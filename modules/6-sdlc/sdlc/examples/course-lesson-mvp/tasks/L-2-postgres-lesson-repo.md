---
id: L-2
epic: course-lesson-mvp
project: BeerLMS
wave: 2
priority: Must
estimate: 1.5d
aggregate: lessons
blocks: [L-3, L-4, L-5, L-6, C-6, CMP-1, CMT-1, E-1, E-2, E-3]
blocked_by: [F-1, L-1]
status: todo
context_budget: ~4500 tokens
created: 2026-05-25
prd_refs: [AC-03, AC-04, AC-04b, AC-07, AC-08, AC-10]
sad_refs: ["§6 US-02", "§6 US-04"]
openapi_paths: []
adr_refs: []
---

# L-2 · `PostgresLessonRepository` (5 methods + blocks JOIN + UNIQUE→ErrSequenceConflict translation)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 1.5d
**Wave:** 2 (domain + repo)

## Місце в послідовності

- **Блокується:** F-1 (chain), L-1 (domain types).
- **Блокує:** усі L-* handler-и + C-6 (reorder читає lessons by course), CMP-1 / CMT-1 (cross-aggregate fetch parent lesson), E-1..E-3.
- **Чому в цій хвилі:** persistence — gate перед handler-ами. Single repo із усіма методами — один test harness.

## Why (user story)

As a backend developer, I want a single `PostgresLessonRepository` з методами `CreateDraft`, `AddBlock`, `Publish`, `GetByIDWithBlocks`, `ListByCourse`, `ReorderBatch`, плюс UNIQUE-violation translation (`pq.unique_violation` → `ErrSequenceConflict`), so that handler-и не дублюють SQL і завжди filter через JOIN `courses.org_id = $1`.

PRD: AC-04b (no app-level lock, DB UNIQUE), AC-07/AC-08/AC-10 (org-filter + existence-hiding).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-02-addlesson-block-based]], [[../sad.md#us-04-getcourse]]
- 🗄  Data delta:  inherits MIG-1 (`lessons` + `lesson_blocks` у migration 000021)
- 🌐 API contract: [[../contracts/openapi.yaml]] — `Lesson`, `LessonWithBlocks`, `LessonListResponse`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-03, AC-04, AC-04b, AC-07, AC-08, AC-10
- 🧬 Parity ref:   `mentorship/infra/session_repo.go` (cursor pagination + org-scoped + unique-violation handling pattern)

## Data delta

```
NO DB CHANGES — schema у migration 000021.

Queries (всі WHERE через JOIN courses для org-filter):
  CreateDraft (with auto-sequence):
    BEGIN
      seq := SELECT COALESCE(MAX(sequence), 0) + 1 FROM lessons WHERE course_id=$1
      INSERT INTO lessons (...) VALUES (..., seq, ...)
    COMMIT
    Note: явний sequence з request — без COALESCE, через INSERT прямо; UNIQUE constraint вирішить конфлікт.

  AddBlock (with auto-sequence within lesson):
    Same pattern як CreateDraft але table=lesson_blocks, key=lesson_id.

  Publish (всередині caller-tx для F-2 outbox):
    UPDATE lessons SET status='published', published_at=now()
      FROM courses
      WHERE lessons.id = $1
        AND lessons.course_id = courses.id
        AND courses.org_id = $2
        AND lessons.status = 'draft'
      RETURNING lessons.*

  GetByIDWithBlocks:
    SELECT l.*, jsonb_agg(b.*) FROM lessons l
      JOIN courses c ON c.id = l.course_id
      LEFT JOIN lesson_blocks b ON b.lesson_id = l.id
      WHERE l.id = $1 AND c.org_id = $2
      GROUP BY l.id

  ListByCourse (cursor):
    SELECT l.* FROM lessons l
      JOIN courses c ON c.id = l.course_id
      WHERE c.org_id = $1 AND ($2::uuid IS NULL OR l.course_id = $2)
        AND (l.id > $3 OR $3 IS NULL)
      ORDER BY l.id ASC LIMIT $4 + 1

  ReorderBatch (used by C-6):
    BEGIN
      UPDATE lessons SET sequence=$2 WHERE id=$1   -- repeat per item
    COMMIT
    Note: UNIQUE(course_id, sequence) — батч може зіткнутися із самим собою (наприклад swap 1↔2). Mitigation: 2-phase update (set negative temp, then final) — known pattern; details у C-6.
```

## API contract

_No HTTP._

```go
type Repository interface {
  CreateDraft(ctx, l Lesson) (Lesson, error)
  AddBlock(ctx, b LessonBlock) (LessonBlock, error)
  Publish(ctx, orgID, lessonID uuid.UUID, tx pgx.Tx) (Lesson, bool /*alreadyPublished*/, error)
  GetByIDWithBlocks(ctx, orgID, lessonID uuid.UUID) (Lesson, []LessonBlock, error)
  ListByCourse(ctx, orgID uuid.UUID, courseID *uuid.UUID, after *uuid.UUID, limit int) ([]Lesson, bool, error)
  ReorderBatch(ctx, orgID, courseID uuid.UUID, items []ReorderItem, tx pgx.Tx) error
  CountBlocks(ctx, lessonID uuid.UUID) (int, error)  // used by L-6 publish gate
}
```

## Acceptance criteria (GWT)

- [ ] **AC-l2-1 (CreateDraft auto-sequence):** Given course із 0 lessons, when CreateDraft(lesson із sequence=0 placeholder), then row INSERT-нуто із sequence=1. Другий call → sequence=2.
- [ ] **AC-l2-2 (CreateDraft explicit sequence):** Given lesson із explicit sequence=5, when CreateDraft, then INSERT з sequence=5; happy path.
- [ ] **AC-l2-3 (UNIQUE violation translation — AC-04b):** Given lesson із sequence=2 існує, when CreateDraft іншого lesson із sequence=2 на той самий course, then `pq.unique_violation` → `domain.ErrSequenceConflict`. (Через `errors.As` на `*pgconn.PgError` із code `23505`.)
- [ ] **AC-l2-4 (AddBlock з auto-sequence within lesson):** Analogously to AC-l2-1 але для blocks.
- [ ] **AC-l2-5 (BlockSequenceConflict):** Same as AC-l2-3 але для `lesson_blocks` UNIQUE → `domain.ErrBlockSequenceConflict`.
- [ ] **AC-l2-6 (Publish happy):** Given draft lesson із blocks count > 0, when Publish(orgID, lessonID, tx) всередині caller-tx, then UPDATE-ить status; returns `(lesson, alreadyPublished=false, nil)`.
- [ ] **AC-l2-7 (Publish idempotent):** Given already-published lesson, when Publish called, then no UPDATE; SELECT current; returns `(lesson, alreadyPublished=true, nil)`.
- [ ] **AC-l2-8 (Publish cross-org):** Given lesson у org Y, when Publish(orgX, id, tx), then `ErrLessonNotFound`.
- [ ] **AC-l2-9 (GetByIDWithBlocks happy):** Given lesson із 3 blocks ordered by sequence, when GetByIDWithBlocks, then returns lesson + 3 blocks sorted ASC by sequence.
- [ ] **AC-l2-10 (GetByIDWithBlocks cross-org — AC-07):** Cross-org access → `ErrLessonNotFound` (existence-hiding).
- [ ] **AC-l2-11 (ListByCourse cursor + filter):** Given courseID provided у query → filters by course; nil → all lessons in caller's org.
- [ ] **AC-l2-12 (ListByCourse cross-org isolation):** Org Y's lessons не returned.
- [ ] **AC-l2-13 (CountBlocks):** Given lesson із 5 blocks, when CountBlocks, then 5.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/lessons/ports/repository.go` із interface вище + `ReorderItem` struct.
- [ ] Step 2 — Створити `beer-lms-api/internal/modules/lessons/infra/postgres_lesson_repo.go`. Constructor: `NewPostgresLessonRepository(db *database.DB) *PostgresLessonRepository`.
- [ ] Step 3 — Реалізувати усі 7 методів. Усі SELECT/UPDATE проходять через JOIN на `courses` для org-filter.
- [ ] Step 4 — Auto-sequence у CreateDraft / AddBlock: якщо `l.Sequence == 0` → SELECT MAX+1 у тій самій tx (race acceptable — UNIQUE спіймає конфлікт).
- [ ] Step 5 — UNIQUE-violation translation: helper `translatePgErr(err, conflictName)` мапить pgcode `23505` → `ErrSequenceConflict` / `ErrBlockSequenceConflict` залежно від constraint name (parse pq error message).
- [ ] Step 6 — `Publish` та `ReorderBatch` приймають `pgx.Tx` (для F-2 outbox у L-6 + atomic reorder у C-6).
- [ ] Step 7 — Integration tests `postgres_lesson_repo_test.go` через testcontainers — покрити AC-l2-1..AC-l2-13.
- [ ] Step 8 — Add tests "cross-org draft lesson не видно для іншого org-овського каллера" і "draft for non-owner у тій же org — repo поверне рядок (handler фільтрує по owner)".

## Edge cases

| Кейс | Поведінка |
|---|---|
| `pq.unique_violation` із constraint name = `lessons_course_id_sequence_key` | Translate в `ErrSequenceConflict`. |
| Constraint name = `lesson_blocks_lesson_id_sequence_key` | Translate в `ErrBlockSequenceConflict`. |
| Concurrent `Publish` || Двох викликів — UPDATE row-lock серіалізує; перший win, другий бачить 0 affected → SELECT current, повертає alreadyPublished=true. |
| GetByIDWithBlocks для lesson без blocks | Returns lesson + empty `[]LessonBlock{}`. NOT nil. |
| `ReorderBatch` із дуплікатом sequence у payload | Перший UPDATE OK, другий conflict → tx rollback → `ErrSequenceConflict`. Caller (C-6) має 2-phase pattern якщо потрібен swap. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Integration tests через testcontainers покривають усі 7 методів + cross-org isolation.
- [ ] `go vet` + `golangci-lint run` clean у `internal/modules/lessons/`.
- [ ] Coverage ≥ 85% у `infra/`.
- [ ] PR linked back to `tasks/L-2-postgres-lesson-repo.md`.
- [ ] `tracker.md` оновлено: status `done`.
