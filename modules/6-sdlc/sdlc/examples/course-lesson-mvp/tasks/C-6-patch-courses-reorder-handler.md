---
id: C-6
epic: course-lesson-mvp
project: BeerLMS
wave: 3
priority: Must
estimate: 0.5d
aggregate: courses
blocks: []
blocked_by: [C-2, L-2]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: []
sad_refs: ["§6 US-05"]
openapi_paths: ["PATCH /courses/{id}/lessons/reorder"]
adr_refs: []
---

# C-6 · `PATCH /courses/{id}/lessons/reorder` handler (US-05 reorder)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 3 (handlers)

## Місце в послідовності

- **Блокується:** C-2 (course state check — draft only), L-2 (`ReorderBatch` method).
- **Блокує:** нічим (no E2E covers reorder у v1 — out of E-1 scope).
- **Чому в цій хвилі:** simple handler, паралельний з іншими.

## Why (user story)

As a `methodist`, I want to reorder lessons у моєму draft course (sequence editable до публікації course), so that I can fix lesson ordering before going live without manual workaround.

PRD US-05. PRD §6.1 abuse-case 5 (reorder DoS — bound payload ≤ 50). openapi mandates ≤ 50 items.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-05-reorder]]
- 🗄  Data delta:  none — UPDATE on existing `lessons.sequence`.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `PATCH /courses/{id}/lessons/reorder` (`reorderCourseLessons`)
- 📜 Relevant ADR: none
- 📋 PRD ACs:      US-05 + PRD §6.1 abuse case 5 (no specific AC-NN — covered by openapi error mapping)

## Data delta

```
NO new tables. UPDATE-batch у `lessons`.

Pattern (2-phase для swap-safe):
  BEGIN
    SELECT course.status — if 'published' → ROLLBACK + 409 course.already_published
    UPDATE lessons SET sequence = -sequence WHERE id IN (...)    -- phase 1: negative temp
    UPDATE lessons SET sequence = <new> WHERE id = <id>          -- phase 2: per-item
  COMMIT
```

## API contract

```
PATCH /courses/{id}/lessons/reorder
  AuthN: BearerAuth
  AuthZ: caller == course_owner (else 404 collapse)
  Body: ReorderLessonsRequest {items: [{lesson_id, sequence}], maxItems 50}
  Response:
    200 ReorderLessonsResponse
    400 validation.reorder_payload_too_large  (items > 50)
    401 auth.unauthorized
    404 course.not_found
    409 course.already_published
    409 lesson.sequence_conflict              (duplicate sequence у batch)
```

## Acceptance criteria (GWT)

- [ ] **AC-c6-1 (happy reorder swap):** Given course із lessons [A:1, B:2, C:3], owner caller, when PATCH із items [{B, 1}, {A, 2}], then 200; DB: A:2, B:1, C:3.
- [ ] **AC-c6-2 (payload > 50):** Given items length 51, when PATCH, then 400 `validation.reorder_payload_too_large`.
- [ ] **AC-c6-3 (published course):** Given course status='published', when PATCH, then 409 `course.already_published`.
- [ ] **AC-c6-4 (duplicate sequence у batch):** Given items [{A,1}, {B,1}], when PATCH, then 409 `lesson.sequence_conflict`; DB unchanged (rollback).
- [ ] **AC-c6-5 (non-owner):** Given caller ≠ course_owner, when PATCH, then 404 `course.not_found`.
- [ ] **AC-c6-6 (cross-org):** Given course у org Y, when caller з org X PATCHes, then 404.
- [ ] **AC-c6-7 (items references foreign lesson):** Given item.lesson_id належить course Z (не path course), when PATCH, then 404 `lesson.not_found` (validation prerequisite — або treat ↻ 0-affected UPDATE).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `ReorderLessons(ctx, orgID, userID, courseID uuid.UUID, items []ReorderItem) error`.
- [ ] Step 2 — Service flow:
   1. `coursesRepo.GetByID(orgID, courseID)` → 404 if missing.
   2. If caller != course_owner → 404.
   3. If course.status == "published" → 409 `course.already_published`.
   4. Validate items length ≤ 50 (handler-side).
   5. Validate items unique by lesson_id AND unique by sequence (early-fail vs DB UNIQUE).
   6. BEGIN tx.
   7. `lessonsRepo.ReorderBatch(orgID, courseID, items, tx)` — 2-phase update.
   8. COMMIT.
- [ ] Step 3 — Handler `PatchReorderLessons(w, r)` — реєструвати path.
- [ ] Step 4 — Тесtи: AC-c6-1..AC-c6-7 + edge-case "1-item reorder" (no-op).

## Edge cases

| Кейс | Поведінка |
|---|---|
| Items reference lesson belonging to course із іншої org | `ReorderBatch` repo-метод фільтрує `WHERE course_id = $1` — affected=0 → handler може detect-нути і повернути 404 `lesson.not_found` або просто продовжити (no-op). Обираємо detection: 404 (більш чесно). |
| Empty items array | 400 `validation.invalid_payload` (openapi minItems: 1). |
| Items references same lesson двічі | 400 `validation.invalid_payload` (handler-side dedup check). |
| sequence < 1 | 400 `validation.invalid_payload` (openapi minimum: 1). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Service tests + handler tests; coverage ≥ 80%.
- [ ] Integration test із 2-phase swap (testcontainers).
- [ ] OpenAPI Swagger UI показує endpoint.
- [ ] PR linked back to `tasks/C-6-patch-courses-reorder-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
