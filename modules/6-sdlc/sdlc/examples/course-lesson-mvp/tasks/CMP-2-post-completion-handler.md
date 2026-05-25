---
id: CMP-2
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.5d
aggregate: completions
blocks: [E-2]
blocked_by: [CMP-1]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-11, AC-12]
sad_refs: ["§6 US-06"]
openapi_paths: ["POST /lessons/{id}/completion"]
adr_refs: []
---

# CMP-2 · `POST /lessons/{id}/completion` handler (idempotent через UNIQUE)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 4

## Місце в послідовності

- **Блокується:** CMP-1 (repo).
- **Блокує:** E-2 (E2E peer-signal flow стартує з completion).
- **Чому в цій хвилі:** проста handler-story після domain+repo.

## Why (user story)

As a `member`, I want to mark lesson as completed (explicit action), so that я маю personal progress recall, і methodist отримує engagement signal через peer-blob.

PRD US-06. AC-11 (first POST → 201, repeat → 200 same completed_at), AC-12 (draft/cross-org → 404).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-06-completelesson]]
- 🗄  Data delta:  none — INSERT у lesson_completions.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /lessons/{id}/completion`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-11, AC-12

## Data delta

```
INSERT ON CONFLICT DO NOTHING. Org_id inherited from parent lesson's course.
```

## API contract

```
POST /lessons/{id}/completion
  AuthN: BearerAuth
  AuthZ: orgmw + lesson.status == 'published' AND lesson.org == caller.org
  Response:
    201 LessonCompletion  (first completion)
    200 LessonCompletion  (idempotent re-completion)
    401 auth.unauthorized
    404 lesson.not_found  (draft, cross-org, missing)
```

## Acceptance criteria (GWT)

- [ ] **AC-cmp2-1 (first — AC-11 happy):** Given published lesson same org, when POST, then 201 + LessonCompletion із fresh completed_at; row у DB.
- [ ] **AC-cmp2-2 (repeat — AC-11 idempotent):** Given previous POST OK, when retry, then 200 + LessonCompletion із unchanged completed_at; no new row.
- [ ] **AC-cmp2-3 (draft lesson — AC-12):** Given lesson status=draft, when POST, then 404 `lesson.not_found`.
- [ ] **AC-cmp2-4 (cross-org — AC-12):** Given published lesson у org Y, caller у org X, when POST, then 404.
- [ ] **AC-cmp2-5 (missing lesson):** 404.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `CompleteLesson(ctx, orgID, userID, lessonID uuid.UUID) (LessonCompletion, bool /*isNew*/, error)`.
- [ ] Step 2 — Flow:
   1. `lessonsRepo.GetByIDWithBlocks(orgID, lessonID)` (or lighter getter) → 404 if missing.
   2. If lesson.status != published → 404 (collapse for AC-12).
   3. `completion := NewCompletion(userID, lessonID, orgID)`.
   4. `repo.Insert(completion)` → returns final + isNew.
   5. Return (completion, isNew).
- [ ] Step 3 — Handler `PostLessonCompletion(w, r)`. Status code = 201 if isNew else 200.
- [ ] Step 4 — Тести: AC-cmp2-1..AC-cmp2-5.

## Edge cases

| Кейс | Поведінка |
|---|---|
| User не member of org (org_id у lesson != caller.org) | Через orgmw + 404 collapse — never reaches DB write. |
| `lesson.status` race: published → unpublished mid-call | Unpublish не у v1; ризик low. Treat як normal. |
| Multiple completions у різних orgs (user member of two) | Кожна окрема row — UNIQUE(user_id, lesson_id) глобальна, але lesson_id різні per-org (lessons не дублюються між org-ами). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] OpenAPI Swagger UI показує endpoint.
- [ ] PR linked back to `tasks/CMP-2-post-completion-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
