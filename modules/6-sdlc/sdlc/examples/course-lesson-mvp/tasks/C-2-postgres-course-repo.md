---
id: C-2
epic: course-lesson-mvp
project: BeerLMS
wave: 2
priority: Must
estimate: 1d
aggregate: courses
blocks: [C-3, C-4, C-5, C-6, L-3, E-1]
blocked_by: [F-1, C-1]
status: todo
context_budget: ~4000 tokens
created: 2026-05-25
prd_refs: [AC-01, AC-05, AC-07, AC-08, AC-10]
sad_refs: ["§6 US-01", "§6 US-03", "§6 US-04"]
openapi_paths: []
adr_refs: []
---

# C-2 · `PostgresCourseRepository` (5 methods) + integration tests

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 1d
**Wave:** 2 (domain + repo)

## Місце в послідовності

- **Блокується:** F-1 (DI injects checker into handler, not repo, but kept for chain clarity), C-1 (domain types).
- **Блокує:** усі C-* handler-и + L-3 (handler `POST /courses/{id}/lessons` робить cross-aggregate fetch на parent course) + E-1 (E2E через handler-и).
- **Чому в цій хвилі:** persistence — gate перед handler-ами. Усі 5 методів — один test harness.

## Why (user story)

As a backend developer, I want a single `PostgresCourseRepository` із 5 методами (`Create`, `GetByID`, `List`, `Publish`, `CountPublishedLessons`), so that handler-и не дублюють SQL і завжди filter `WHERE org_id = $1` (org-scoped read pattern, mentorship parity).

PRD: AC-01 (create), AC-05 (publish gate — `≥1 published lesson`), AC-07/AC-08 (existence-hiding на cross-org + draft), AC-10 (cross-org parent → 404).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-01-createcourse]], [[../sad.md#us-03-publishcourse]], [[../sad.md#us-04-getcourse]]
- 🗄  Data delta:  inherits MIG-1 (table `courses` у migration 000021)
- 🌐 API contract: [[../contracts/openapi.yaml]] — `Course`, `CourseListResponse`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-01, AC-05, AC-07, AC-08, AC-10
- 🧬 Parity ref:   `mentorship/infra/session_repo.go` (org-scoped reads, cursor pagination)

## Data delta

```
NO DB CHANGES — schema у migration 000021 (already merged).

Queries:
  Create:                INSERT INTO courses (...) VALUES (...)
  GetByID:               SELECT ... FROM courses WHERE id = $1 AND org_id = $2
  List (cursor):         SELECT ... FROM courses WHERE org_id = $1
                           AND (id > $2 OR $2 IS NULL)
                           ORDER BY id ASC LIMIT $3 + 1
  Publish:               UPDATE courses SET status='published', published_at=now()
                           WHERE id=$1 AND org_id=$2 AND status='draft'
                         RETURNING *
  CountPublishedLessons: SELECT count(*) FROM lessons WHERE course_id=$1 AND status='published'
```

## API contract

_No HTTP. Internal Go interface consumed by C-3..C-6._

```go
type Repository interface {
  Create(ctx, c Course) (Course, error)
  GetByID(ctx, orgID, courseID uuid.UUID) (Course, error)  // returns ErrCourseNotFound if cross-org OR not exists
  List(ctx, orgID uuid.UUID, after *uuid.UUID, limit int) ([]Course, bool, error)
  Publish(ctx, orgID, courseID uuid.UUID, tx pgx.Tx) (Course, bool /*alreadyPublished*/, error)
  CountPublishedLessons(ctx, courseID uuid.UUID) (int, error)
}
```

## Acceptance criteria (GWT)

- [ ] **AC-c2-1 (Create happy):** Given valid Course struct, when `Create(c)`, then INSERT-нуто row; returns поверне persisted Course із timestamps (server-side now()).
- [ ] **AC-c2-2 (GetByID happy):** Given course exists у org X, when `GetByID(X, id)` from same org, then returns Course; from different org → `ErrCourseNotFound` (existence-hiding для AC-07).
- [ ] **AC-c2-3 (GetByID — draft visibility delegated up):** GetByID НЕ перевіряє course_owner / admin — це responsibility handler-а (AC-08 logic). Repo лише org-filter.
- [ ] **AC-c2-4 (List cursor):** Given 25 courses у org X (UUID v7 ordered), when List(X, after=nil, limit=10), then returns 10 + `has_next=true`; with `after=last10.id, limit=10` → next 10.
- [ ] **AC-c2-5 (List cross-org isolation):** Given 5 courses у org X + 3 courses у org Y, when List(X, nil, 100), then returns 5 (org Y невидимий).
- [ ] **AC-c2-6 (Publish happy):** Given draft course, when `Publish(orgID, id, tx)` всередині caller-tx, then UPDATE-ить status to published; returns `(course, alreadyPublished=false, nil)`.
- [ ] **AC-c2-7 (Publish idempotent):** Given already-published course, when Publish called, then no UPDATE (WHERE status='draft' returns 0 rows); SELECT current row; returns `(course, alreadyPublished=true, nil)`.
- [ ] **AC-c2-8 (Publish cross-org):** Given course у org Y, when Publish(orgX, id, tx), then `ErrCourseNotFound`.
- [ ] **AC-c2-9 (CountPublishedLessons):** Given course із 3 published lessons + 2 drafts, when CountPublishedLessons(courseID), then 3.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/courses/ports/repository.go` із interface (вгорі).
- [ ] Step 2 — Створити `beer-lms-api/internal/modules/courses/infra/postgres_course_repo.go`. Сигнатура constructor: `NewPostgresCourseRepository(db *database.DB) *PostgresCourseRepository`.
- [ ] Step 3 — Реалізувати `Create`, `GetByID`, `List`, `Publish`, `CountPublishedLessons`.
- [ ] Step 4 — `Publish` приймає `pgx.Tx` (для F-2 outbox у тій самій tx). Якщо UPDATE returns 0 rows із status='draft' filter → re-SELECT і поверни `alreadyPublished=true`.
- [ ] Step 5 — Mapping: `pgx.ErrNoRows` → `domain.ErrCourseNotFound`.
- [ ] Step 6 — Integration tests `postgres_course_repo_test.go` через testcontainers — покрити AC-c2-1..AC-c2-9.
- [ ] Step 7 — Окремий тест "cross-org draft не видно" (mirror того, що `mentorship/infra/session_repo_test.go` робить для sessions).

## Edge cases

| Кейс | Поведінка |
|---|---|
| `pq.unique_violation` на INSERT (немає UNIQUE у courses → не повинно статися) | Не оброблюємо; bubble як generic DB error. |
| Concurrent Publish || Двох викликів — обидва побачать draft, обидва SET status, обидва COMMIT. PostgreSQL row-level lock на UPDATE → послідовні. Перший win, другий бачить 0 affected → alreadyPublished branch. |
| GetByID із `orgID=uuid.Nil` | Filter `WHERE org_id = uuid.Nil` поверне 0 rows → `ErrCourseNotFound`. Caller має validate. |
| List limit > 100 | Repo не валідує — caller (handler) має enforce у openapi (`maximum: 100`). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Integration tests через testcontainers; покривають усі 5 методів.
- [ ] `go vet` + `golangci-lint run` clean у `internal/modules/courses/`.
- [ ] Coverage ≥ 85% у `infra/`.
- [ ] PR linked back to `tasks/C-2-postgres-course-repo.md`.
- [ ] `tracker.md` оновлено: status `done`.
