---
id: L-4
epic: course-lesson-mvp
project: BeerLMS
wave: 3
priority: Must
estimate: 0.75d
aggregate: lessons
blocks: [E-1, CMP-4]
blocked_by: [L-2]
status: todo
context_budget: ~3000 tokens
created: 2026-05-25
prd_refs: [AC-07, AC-08]
sad_refs: ["§6 US-04"]
openapi_paths: ["GET /lessons", "GET /lessons/{id}"]
adr_refs: []
---

# L-4 · `GET /lessons` + `GET /lessons/{id}` handlers (existence-hiding, no peer-signal yet)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.75d
**Wave:** 3 (handlers)

## Місце в послідовності

- **Блокується:** L-2 (repo `GetByIDWithBlocks`, `ListByCourse`).
- **Блокує:** E-1 (E2E reads), CMP-4 (`extend GET /lessons/{id}` із `peer_completion` blob — extension story).
- **Чому в цій хвилі:** read endpoints без peer-signal (peer додається CMP-4 — окремий PR щоб не змішувати).

## Why (user story)

As a `member`, I want to view lessons within my org with proper draft/published visibility, so that внутрішня структура чужих org не leak-ається.

PRD US-04. AC-07/AC-08 на lesson level (mirror course logic). Peer-signal blob додає CMP-4 — НЕ у scope цієї story.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-04-getcourse]] (lesson-mirror)
- 🗄  Data delta:  none — read-only.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `GET /lessons` (`listLessons`), `GET /lessons/{id}` (`getLesson`), `LessonWithBlocks`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-07, AC-08

## Data delta

```
NO writes. SELECT lessons WITH org-filter через JOIN courses + LEFT JOIN blocks.
```

## API contract

```
GET /lessons?course_id=<uuid>&after=<uuid>&limit=<n>
  AuthN: BearerAuth
  AuthZ: orgmw + handler-side draft visibility filter (only owner/admin sees draft)
  Response: 200 LessonListResponse

GET /lessons/{id}
  AuthN: BearerAuth
  AuthZ: orgmw + handler-side visibility check
  Response:
    200 LessonWithBlocks (без peer_completion у цій story — додає CMP-4)
    401 auth.unauthorized
    404 lesson.not_found  (cross-org OR draft-without-perm)
```

## Acceptance criteria (GWT)

- [ ] **AC-l4-1 (list happy):** Given 3 published lessons у org, when GET /lessons, then 200 + 3 items.
- [ ] **AC-l4-2 (list filters foreign drafts):** Given drafts owned by methodist X (caller is інший member), when GET, then drafts X — excluded.
- [ ] **AC-l4-3 (list cross-org isolation):** Given lessons у org Y, when caller у org X GETs, then 0 з Y.
- [ ] **AC-l4-4 (list by course_id filter):** Given course A has 5 lessons, course B has 3, when GET ?course_id=A, then 5.
- [ ] **AC-l4-5 (get published happy):** Given published lesson, when GET, then 200 + Lesson + blocks ordered ASC. `peer_completion` поле відсутнє (додається CMP-4).
- [ ] **AC-l4-6 (get cross-org — AC-07):** Cross-org → 404.
- [ ] **AC-l4-7 (get draft as course_owner):** 200.
- [ ] **AC-l4-8 (get draft as admin):** 200.
- [ ] **AC-l4-9 (get draft as random member — AC-08):** 404.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `GetLessonWithBlocks(ctx, orgID, userID, lessonID)` і `ListLessons(ctx, orgID, userID, courseID, after, limit)`.
- [ ] Step 2 — `GetLessonWithBlocks` flow: `lessonsRepo.GetByIDWithBlocks(orgID, lessonID)` → if missing → 404. Якщо status=draft → fetch parent course → if caller != course_owner AND !IsAdmin → return ErrLessonNotFound (collapse).
- [ ] Step 3 — `ListLessons` flow: `lessonsRepo.ListByCourse(orgID, courseIDPtr, after, limit+1)` → filter drafts де parent course_owner != caller AND !IsAdmin. has_next.
- [ ] Step 4 — HTTP handlers `GetLessons(w,r)`, `GetLesson(w,r)`.
- [ ] Step 5 — Response shape: для `GET /lessons/{id}` повертати `LessonWithBlocks` BUT БЕЗ поля `peer_completion` (omitempty). Document що CMP-4 додає це поле; цей story делегує його.
- [ ] Step 6 — Тести: AC-l4-1..AC-l4-9 + golden response.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Lesson з 0 blocks | Returns `{..., blocks: []}` — empty array, not omit. |
| `course_id` query — invalid UUID | 400 `validation.invalid_query_param`. |
| List cursor — invalid UUID | 400 `validation.invalid_cursor`. |
| GET on non-existent lesson | 404 `lesson.not_found` (existence-hiding default). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] OpenAPI Swagger UI показує обидва endpoints.
- [ ] PR linked back to `tasks/L-4-get-lessons-handlers.md`.
- [ ] `tracker.md` оновлено: status `done`.
