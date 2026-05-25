---
id: C-1
epic: course-lesson-mvp
project: BeerLMS
wave: 2
priority: Must
estimate: 0.5d
aggregate: courses
blocks: [C-2, C-3, C-4, C-5, C-6]
blocked_by: [F-1]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-01, AC-02, AC-05, AC-06]
sad_refs: ["§6 US-01", "§6 US-03"]
openapi_paths: []
adr_refs: []
---

# C-1 · `Course` domain entity + sentinel errors + factory

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 2 (domain + repo)

## Місце в послідовності

- **Блокується:** F-1 (потрібні role-checkers для handler-ів, але domain сам по собі не залежить; кладу dep щоб уся courses chain мала ясний gate). Може landed-itися паралельно з L-1.
- **Блокує:** C-2 (repo читає domain types), всі C-3..C-6 handler-и.
- **Чому в цій хвилі:** pure Go types — domain shape для всіх courses operations.

## Why (user story)

As a `methodist`, I want a `Course` aggregate що capture title, description, cover URL, status, course_owner_id, org_id, published_at + timestamps, so that persistence + HTTP layers мали один типизований model для round-trip.

PRD US-01 (createCourse), US-03 (publishCourse).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-01-createcourse]], [[../sad.md#us-03-publishcourse]]
- 🗄  Data delta:  none — pure domain types; DB schema у migration 000021 (already merged).
- 🌐 API contract: [[../contracts/openapi.yaml]] — schemas `Course`, `CreateCourseRequest`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-01, AC-02, AC-05, AC-06
- 🧬 Parity ref:   mirror `mentorship/domain/session.go` shape (typed status, factory, sentinel errors)

## Data delta

```
NO DB CHANGES IN THIS STORY — pure domain types.
MIG-1 (000020-000022) owns SQL. Story matches data-model.md typed shape:

Course:
  id (UUID v7), org_id (UUID), course_owner_id (UUID),
  title (≤ 200 chars), description (≤ 500 chars, nullable),
  cover_image_url (TEXT nullable), status (enum: draft|published),
  published_at (nullable TIMESTAMPTZ), created_at, updated_at
```

## API contract

_API surface: none — internal story. Domain types are consumed by C-2 / C-3..C-6._

## Acceptance criteria (GWT)

- [ ] **AC-c1-1 (factory happy):** Given valid `org_id`, `course_owner_id`, `title` ≤ 200, when `NewDraftCourse(...)` is called, then returns `Course` із UUID v7 id, status=`draft`, `published_at=nil`, timestamps now UTC.
- [ ] **AC-c1-2 (AC-01 mapping):** Domain factory return-ить структуру з полями що мап-ляться 1:1 на `Course` schema у openapi (без `org_id` у response — це handler-side concern).
- [ ] **AC-c1-3 (AC-02 — description ≤ 500):** Given `description` > 500 chars, when factory called, then returns `ErrDescriptionTooLong`. (Domain валідує length; handler перетворює на `validation.description_too_long` 400.)
- [ ] **AC-c1-4 (title required):** Given `title == ""`, when factory called, then returns `ErrInvalidPayload`.
- [ ] **AC-c1-5 (sentinels exported):** `ErrCourseNotFound`, `ErrCourseAlreadyPublished`, `ErrNoPublishedLessons`, `ErrNotMethodist`, `ErrForbidden`, `ErrDescriptionTooLong`, `ErrInvalidPayload` — exported sentinel errors, matchable через `errors.Is`. Naming convention: `course.<snake>` (mentorship parity).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/courses/domain/course.go` із struct `Course`. Status — typed string з константами `StatusDraft`, `StatusPublished`.
- [ ] Step 2 — Створити `beer-lms-api/internal/modules/courses/domain/errors.go` із усіма sentinels із AC-c1-5. Кожна → `errors.New("course.<snake_case>")` (mentorship convention).
- [ ] Step 3 — Додати factory `NewDraftCourse(orgID, ownerID uuid.UUID, title, description string, coverURL *string) (Course, error)` із UUID v7 generation + validation (title required, title ≤ 200, description ≤ 500 if provided).
- [ ] Step 4 — Додати method `(c *Course) MarkPublished(now time.Time)` — sets status, published_at, updated_at. Returns `ErrCourseAlreadyPublished` if status вже `published`. (idempotent check вищого рівня — у C-5 handler.)
- [ ] Step 5 — Юніт-тести: factory happy + AC-c1-3 + AC-c1-4 + MarkPublished happy + MarkPublished двічі.

## Edge cases

| Кейс | Поведінка |
|---|---|
| `description = ""` (empty string) | Зберігається як NULL у DB (handler конвертує `""` → `nil`); domain приймає `""` без помилки. |
| `cover_image_url` provided | Domain не валідує URL — це OQ-1 / OQ-2 у PRD. Зберігаємо as-is. |
| `MarkPublished` на already published course | Returns `ErrCourseAlreadyPublished` — caller (C-5 handler) трактує як idempotent OK, не як error. |
| Concurrent factory calls із однаковим UUID v7 | Не може статися — UUID v7 monotonic-time-based, collision ймовірність ~0. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] `go vet` + `golangci-lint run` clean у `internal/modules/courses/domain/`.
- [ ] Coverage ≥ 90% у `domain/`.
- [ ] PR linked back to `tasks/C-1-domain-course.md`.
- [ ] `tracker.md` оновлено: status `done`.
