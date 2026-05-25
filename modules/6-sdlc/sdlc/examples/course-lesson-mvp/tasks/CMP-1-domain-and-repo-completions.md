---
id: CMP-1
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.5d
aggregate: completions
blocks: [CMP-2, CMP-3]
blocked_by: [L-2]
status: todo
context_budget: ~3000 tokens
created: 2026-05-25
prd_refs: [AC-11, AC-12]
sad_refs: ["§6 US-06"]
openapi_paths: []
adr_refs: []
---

# CMP-1 · `LessonCompletion` domain + `PostgresLessonCompletionRepository` + tests

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 4 (other aggregates)

## Місце в послідовності

- **Блокується:** L-2 (cross-aggregate fetch parent lesson for org-resolution).
- **Блокує:** CMP-2 (handler), CMP-3 (peer-blob aggregation).
- **Чому в цій хвилі:** менший за courses/lessons; domain + repo разом — 0.5 дня.

## Why (user story)

As a `member`, I want a `LessonCompletion` entity + repo із idempotent insert (UNIQUE(user_id, lesson_id) → re-read on conflict), so that "Mark complete" завжди returns success без duplicate.

PRD US-06. AC-11 (idempotent через UNIQUE), AC-12 (cross-org/draft → 404).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-06-completelesson]]
- 🗄  Data delta:  inherits MIG-1 (`lesson_completions` у migration 000021)
- 🌐 API contract: [[../contracts/openapi.yaml]] — `LessonCompletion` schema
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-11, AC-12
- 🧬 Parity ref:   mirror `mentorship/infra/session_repo.go` org-scoped reads

## Data delta

```
NO DB CHANGES — schema у migration 000021.

Queries:
  Insert (idempotent):
    INSERT INTO lesson_completions (id, user_id, lesson_id, org_id, completed_at, created_at)
      VALUES (...)
      ON CONFLICT (user_id, lesson_id) DO NOTHING
      RETURNING *
    Якщо RETURNING повертає 0 rows (conflict) → SELECT існуючий rows + return flag isNew=false.

  GetByUserLesson:
    SELECT * FROM lesson_completions WHERE user_id=$1 AND lesson_id=$2

  CountByLesson (для CMP-3 peer-blob):
    SELECT count(*) FROM lesson_completions WHERE lesson_id=$1 AND org_id=$2

  RecentByLesson (для CMP-3):
    SELECT lc.*, u.display_name FROM lesson_completions lc
      JOIN user_preferences up ON up.user_id = lc.user_id
      JOIN users u ON u.id = lc.user_id
      WHERE lc.lesson_id=$1 AND lc.org_id=$2 AND up.peer_visibility='public'
      ORDER BY lc.completed_at DESC LIMIT 5
```

## API contract

_No HTTP. Internal Go interface consumed by CMP-2 / CMP-3._

```go
type Repository interface {
  Insert(ctx, c LessonCompletion) (LessonCompletion, bool /*isNew*/, error)
  GetByUserLesson(ctx, userID, lessonID uuid.UUID) (LessonCompletion, error)
  CountByLesson(ctx, lessonID, orgID uuid.UUID) (int, error)
  RecentPublicByLesson(ctx, lessonID, orgID uuid.UUID, limit int) ([]CompleterWithName, error)
}
```

## Acceptance criteria (GWT)

- [ ] **AC-cmp1-1 (factory):** `NewCompletion(userID, lessonID, orgID)` повертає struct із UUID v7, completed_at=now UTC.
- [ ] **AC-cmp1-2 (Insert happy):** First insert → isNew=true; row у DB.
- [ ] **AC-cmp1-3 (Insert idempotent — AC-11):** Repeat call → isNew=false; same `completed_at` returned (no overwrite).
- [ ] **AC-cmp1-4 (CountByLesson scoped to org):** Given 5 completions у org X + 2 у org Y for same lesson, when CountByLesson(lesson, X), then 5.
- [ ] **AC-cmp1-5 (RecentPublicByLesson respects preference):** Given 3 completions: 2 із peer_visibility='public', 1 'private', when RecentPublicByLesson, then 2 returned (private excluded).
- [ ] **AC-cmp1-6 (sentinel errors):** `ErrCompletionNotFound` — exported.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/completions/domain/completion.go` + `errors.go`.
- [ ] Step 2 — Створити `beer-lms-api/internal/modules/completions/ports/repository.go` із interface.
- [ ] Step 3 — Створити `beer-lms-api/internal/modules/completions/infra/postgres_completion_repo.go`.
- [ ] Step 4 — Реалізувати `Insert` через `INSERT ... ON CONFLICT DO NOTHING RETURNING`. Якщо 0 rows → SELECT поточний.
- [ ] Step 5 — Реалізувати CountByLesson + RecentPublicByLesson (JOIN на users + user_preferences).
- [ ] Step 6 — Domain factory + unit tests.
- [ ] Step 7 — Integration tests із testcontainers — AC-cmp1-1..AC-cmp1-6.

## Edge cases

| Кейс | Поведінка |
|---|---|
| User without `user_preferences` row | `RecentPublicByLesson` JOIN excludes them (no row → not public). Compatible із default 'private'. |
| Concurrent insert same (user, lesson) | UNIQUE → second goroutine returns isNew=false. |
| OrgID mismatch on insert | Caller has to provide right org (from parent lesson lookup у handler). Repo doesn't validate. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Integration tests; coverage ≥ 85% у `infra/`.
- [ ] `go vet` + `golangci-lint run` clean.
- [ ] PR linked back to `tasks/CMP-1-domain-and-repo-completions.md`.
- [ ] `tracker.md` оновлено: status `done`.
