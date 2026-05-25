---
id: L-1
epic: course-lesson-mvp
project: BeerLMS
wave: 2
priority: Must
estimate: 1d
aggregate: lessons
blocks: [L-2, L-3, L-4, L-5, L-6]
blocked_by: [F-1]
status: todo
context_budget: ~3500 tokens
created: 2026-05-25
prd_refs: [AC-03, AC-04, AC-04b]
sad_refs: ["§6 US-02"]
openapi_paths: []
adr_refs: [ADR-0001]
---

# L-1 · `Lesson` + `LessonBlock` domain + sentinel errors + factories

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 1d
**Wave:** 2 (domain + repo)

## Місце в послідовності

- **Блокується:** F-1 (chain gate).
- **Блокує:** L-2 (repo reads domain types), L-3..L-6 handler-и, CMP-1 / CMT-1 (cross-aggregate references via lesson_id).
- **Чому в цій хвилі:** pure Go types + sentinel errors. Жодного DB-доступу, жодного HTTP. Може landed-itися паралельно з C-1 і L-2 (різні файли).

## Why (user story)

As a `methodist`, I want a lesson aggregate з title, sequence, status, published_at + ordered list of typed content blocks, so that persistence + HTTP layers мали один типизований model для round-trip.

PRD US-02 (block-based lesson body). Grounds AC-03 / AC-04 / AC-04b в domain shape. Polymorphic block payload per ADR-0001.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-02-addlesson-block-based]]
- 🗄  Data delta:  none — pure domain types. SQL у migration 000021 (already merged).
- 🌐 API contract: [[../contracts/openapi.yaml]] — schemas `Lesson`, `LessonBlock`, `CreateCourseLessonRequest`, `AddBlockRequest`
- 📜 Relevant ADR: [[../adr/0001-content-storage-strategy|ADR-0001]] (polymorphic block payload)
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-03, AC-04, AC-04b
- 🧬 Parity ref:   mirror `mentorship/domain/session.go` shape

## Data delta

```
NO DB CHANGES. Domain shape per data-model.md:

Lesson:
  id (UUID v7), course_id (UUID), sequence (int ≥ 1),
  title (≤ 200 chars), status (enum: draft|published),
  duration_seconds (nullable int, 300..14400),
  published_at (nullable TIMESTAMPTZ), created_at, updated_at

  Note: lesson НЕ має org_id колонки — org-scope через JOIN courses(org_id).

LessonBlock:
  id (UUID v7), lesson_id (UUID), sequence (int ≥ 1),
  block_type (enum: text|video_embed|image|code),
  payload (polymorphic per block_type — ADR-0001 шапа),
  created_at, updated_at
```

## API contract

_API surface: none — internal story._

## Acceptance criteria (GWT)

- [ ] **AC-l1-1 (lesson factory happy):** Given valid `course_id`, `title` ≤ 200, optional `sequence` ≥ 1, when `NewDraftLesson(...)`, then returns Lesson з UUID v7, status=`draft`, `published_at=nil`, timestamps now UTC.
- [ ] **AC-l1-2 (sequence guard derivation — AC-04):** Domain не блокує — два concurrent `NewDraftLesson` із однаковим sequence обидва успішні. Конфлікт виявляє repo (L-2) через DB UNIQUE → translate у `ErrSequenceConflict`.
- [ ] **AC-l1-3 (duration validation):** Given `duration_seconds` < 300 OR > 14400 (provided), when factory called, then `ErrInvalidPayload`.
- [ ] **AC-l1-4 (block_type validation):** Given `block_type` outside {text, video_embed, image, code}, when `NewBlock(...)`, then `ErrInvalidBlockType`.
- [ ] **AC-l1-5 (MarkPublished idempotency):** Given already-published lesson, when `MarkPublished` called second time, then returns `ErrLessonAlreadyPublished`. Handler (L-6) трактує як idempotent OK.
- [ ] **AC-l1-6 (sentinel errors exported):** `ErrLessonNotFound`, `ErrSequenceConflict`, `ErrBlockSequenceConflict`, `ErrForbidden`, `ErrInvalidBlockType`, `ErrInvalidPayload`, `ErrLessonAlreadyPublished`, `ErrNoBlocks` — exported sentinels, matchable через `errors.Is`. Naming: `lesson.<snake>` (mentorship parity).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/lessons/domain/lesson.go` із struct `Lesson`. Status — typed string з константами `StatusDraft`, `StatusPublished`.
- [ ] Step 2 — Створити `beer-lms-api/internal/modules/lessons/domain/lesson_block.go` із struct `LessonBlock`. BlockType — typed string з константами для 4 значень.
- [ ] Step 3 — Створити `beer-lms-api/internal/modules/lessons/domain/errors.go` із sentinels із AC-l1-6. Names: `lesson.not_found`, `lesson.sequence_conflict`, ...
- [ ] Step 4 — Factory `NewDraftLesson(courseID uuid.UUID, title string, sequence *int, durationSeconds *int) (Lesson, error)` із UUID v7 + validation (title ≤ 200; sequence ≥ 1 if provided; duration in [300,14400] if provided).
- [ ] Step 5 — Factory `NewBlock(lessonID uuid.UUID, sequence int, blockType BlockType, payload map[string]any) (LessonBlock, error)` із UUID v7 + block_type enum check.
- [ ] Step 6 — Method `(l *Lesson) MarkPublished(now time.Time) error` — sets status/published_at/updated_at. Returns `ErrLessonAlreadyPublished` if already.
- [ ] Step 7 — Юніт-тести для factories + MarkPublished: всі happy paths + всі validation failures.

## Edge cases

| Кейс | Поведінка |
|---|---|
| `title = ""` | `NewDraftLesson` → `ErrInvalidPayload`. |
| `sequence = nil` (auto-assign) | Domain returns Lesson із `sequence = 0` (placeholder); repo (L-2) assign-ить next-free integer перед INSERT. |
| `block_type = "code"` payload без `language` | Domain не валідує payload shape — це робить handler (L-5). Domain валідує лише `block_type` enum. |
| Concurrent `NewDraftLesson` із однаковим sequence | Domain не блокує — це DB UNIQUE constraint (AC-04b). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] `go vet` + `golangci-lint run` clean у `internal/modules/lessons/domain/`.
- [ ] Coverage ≥ 90% у `domain/`.
- [ ] PR linked back to `tasks/L-1-domain-lesson-block.md`.
- [ ] `tracker.md` оновлено: status `done`.
