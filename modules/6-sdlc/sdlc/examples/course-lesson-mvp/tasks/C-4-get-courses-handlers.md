---
id: C-4
epic: course-lesson-mvp
project: BeerLMS
wave: 3
priority: Must
estimate: 0.75d
aggregate: courses
blocks: [E-1]
blocked_by: [C-2]
status: todo
context_budget: ~3000 tokens
created: 2026-05-25
prd_refs: [AC-07, AC-08]
sad_refs: ["§6 US-04"]
openapi_paths: ["GET /courses", "GET /courses/{id}"]
adr_refs: []
---

# C-4 · `GET /courses` + `GET /courses/{id}` handlers (existence-hiding)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.75d
**Wave:** 3 (handlers)

## Місце в послідовності

- **Блокується:** C-2 (repo).
- **Блокує:** E-1 (E2E reads через цей endpoint).
- **Чому в цій хвилі:** два read endpoints через один code-path — паралельний з іншими handler-ами.

## Why (user story)

As a `member`, I want to browse + view courses у своїй org with proper visibility rules (published — everyone у org; draft — owner+admin only; cross-org → 404), so that внутрішня структура чужих org не leak-ається через API.

PRD US-04. AC-07 (cross-org published → 404 existence-hiding), AC-08 (draft visible only to owner + admin).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-04-getcourse]]
- 🗄  Data delta:  none — read-only.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `GET /courses` (`listCourses`), `GET /courses/{id}` (`getCourse`)
- 📜 Relevant ADR: none
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-07, AC-08

## Data delta

```
NO writes. SELECT from courses with org-filter.
```

## API contract

```
GET /courses?after=<uuid>&limit=<n>
  AuthN: BearerAuth
  AuthZ: orgmw only (read endpoint — будь-який member)
  Response: 200 CourseListResponse {items, has_next, next_cursor?}
  Drafts візібільність — handler-side filter:
    show draft IF (caller == course_owner) OR (IsAdmin(orgID, userID))
    else skip draft.

GET /courses/{id}
  AuthN: BearerAuth
  AuthZ: orgmw + handler-side visibility check
  Response:
    200 Course  (success)
    401 auth.unauthorized
    404 course.not_found  (cross-org OR draft-without-perm — existence-hiding)
```

## Acceptance criteria (GWT)

- [ ] **AC-c4-1 (list happy):** Given 3 published + 2 drafts (owned by caller) у org, when GET /courses, then returns 5 items.
- [ ] **AC-c4-2 (list filters foreign drafts):** Given drafts owned by user X (not caller, not admin), when caller GETs /courses, then drafts X — excluded.
- [ ] **AC-c4-3 (list cross-org isolation):** Given courses у org Y, when caller з org X GETs, then 0 з org Y.
- [ ] **AC-c4-4 (list cursor):** Given 25 published courses, when GET /courses?limit=10, then 10 items + has_next=true; з `after=last10.id, limit=10` → next 10.
- [ ] **AC-c4-5 (get published happy):** Given published course caller's org, when GET /courses/{id}, then 200 + Course.
- [ ] **AC-c4-6 (get cross-org — AC-07):** Given published course у org Y, when caller з org X GETs, then 404 `course.not_found`.
- [ ] **AC-c4-7 (get draft as owner):** Given draft course, when course_owner GETs, then 200.
- [ ] **AC-c4-8 (get draft as admin):** Given draft course, when admin (other than owner) GETs, then 200.
- [ ] **AC-c4-9 (get draft as random member — AC-08):** Given draft course, when caller ≠ owner AND ≠ admin, then 404 `course.not_found`.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `ListCourses(ctx, orgID, userID, after, limit)` і `GetCourse(ctx, orgID, userID, courseID)`. Обидва inject `OrgMemberChecker` для AC-c4-8 / AC-c4-2.
- [ ] Step 2 — `ListCourses` flow: `repo.List(orgID, after, limit+1)` → filter out drafts де owner != userID AND !IsAdmin. Compute `has_next` after filter.
- [ ] Step 3 — `GetCourse` flow: `repo.GetByID(orgID, id)` → on `ErrCourseNotFound` → 404. On found → if status=draft AND owner!=userID AND !IsAdmin → return `ErrCourseNotFound` (collapse to 404 — existence-hiding).
- [ ] Step 4 — HTTP handlers `GetCourses(w,r)`, `GetCourse(w,r)`. Реєструвати paths.
- [ ] Step 5 — Cursor pagination: parse `after` як UUID; `limit` parse + clamp [1, 100] (default 20).
- [ ] Step 6 — Handler tests: AC-c4-1..AC-c4-9 + golden response shape.

## Edge cases

| Кейс | Поведінка |
|---|---|
| `after` — invalid UUID | 400 `validation.invalid_cursor`. |
| `limit` > 100 | Clamp to 100 (silent). |
| `limit` < 1 | 400 `validation.invalid_limit` OR clamp to 1 — обираємо clamp для UX (mentorship parity). |
| List із 0 items | 200 `{items: [], has_next: false, next_cursor: null}`. |
| GET on UUID, що не існує взагалі | 404 `course.not_found`. Не розрізняємо "not exists" vs "cross-org" — existence-hiding default. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] OpenAPI Swagger UI показує обидва endpoints.
- [ ] PR linked back to `tasks/C-4-get-courses-handlers.md`.
- [ ] `tracker.md` оновлено: status `done`.
