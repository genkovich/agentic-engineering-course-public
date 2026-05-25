---
id: L-3
epic: course-lesson-mvp
project: BeerLMS
wave: 3
priority: Must
estimate: 0.75d
aggregate: lessons
blocks: [E-1]
blocked_by: [L-2, C-2]
status: todo
context_budget: ~3000 tokens
created: 2026-05-25
prd_refs: [AC-03, AC-04, AC-04b, AC-10]
sad_refs: ["§6 US-02"]
openapi_paths: ["POST /courses/{id}/lessons"]
adr_refs: []
---

# L-3 · `POST /courses/{course_id}/lessons` handler (createCourseLesson — preferred US-02 route)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.75d
**Wave:** 3 (handlers)

## Місце в послідовності

- **Блокується:** L-2 (lesson repo), C-2 (parent course fetch — `AC-10 cross-org guard`).
- **Блокує:** E-1 (E2E через цей endpoint).
- **Чому в цій хвилі:** primary US-02 route. Деpрекований `POST /lessons` openapi (без слешу) — НЕ у scope (lazy migration, можна додати окремо).

## Why (user story)

As a `methodist`, I want to create a lesson under a course через nested path `POST /courses/{course_id}/lessons`, so that route reflects ownership hierarchy і не дублює `course_id` у body.

PRD US-02. AC-03 (happy), AC-04 (explicit sequence conflict), AC-04b (concurrent conflict via DB UNIQUE), AC-10 (cross-org parent → 404).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-02-addlesson-block-based]]
- 🗄  Data delta:  none — schema у MIG-1.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /courses/{id}/lessons` (`createCourseLesson`), `CreateCourseLessonRequest`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-03, AC-04, AC-04b, AC-10

## Data delta

```
INSERT-only into `lessons`. Sequence auto-assigned if not provided.
```

## API contract

```
POST /courses/{course_id}/lessons
  AuthN: BearerAuth
  AuthZ: orgmw + IsMethodist + caller == course_owner of parent
         else → 404 course.not_found (existence-hiding)
  Body: CreateCourseLessonRequest {title, sequence?, duration_seconds?}
  Response:
    201 Lesson
    400 lesson.invalid_payload
    401 auth.unauthorized
    403 course.not_methodist
    404 course.not_found              (AC-10 cross-org parent)
    409 lesson.sequence_conflict       (AC-04 / AC-04b)
```

## Acceptance criteria (GWT)

- [ ] **AC-l3-1 (happy — AC-03):** Given valid body, methodist caller, owns parent course (own org), when POST, then 201 + Lesson (status=draft, sequence assigned, course_id=path).
- [ ] **AC-l3-2 (auto-sequence):** Given course із lessons [seq 1, 2], no sequence у body, when POST, then 201 із sequence=3.
- [ ] **AC-l3-3 (explicit sequence conflict — AC-04):** Given lesson із sequence=2 existing, when POST з sequence=2, then 409 `lesson.sequence_conflict`.
- [ ] **AC-l3-4 (concurrent — AC-04b):** Given two parallel POSTs з explicit same sequence, when both run, then one 201, other 409 `lesson.sequence_conflict` (DB UNIQUE).
- [ ] **AC-l3-5 (non-methodist):** Given caller без is_methodist, when POST, then 403 `course.not_methodist`.
- [ ] **AC-l3-6 (cross-org parent — AC-10):** Given course у org Y, caller у org X, when POST, then 404 `course.not_found`.
- [ ] **AC-l3-7 (non-owner methodist у тій же org):** Given course owned by methodist X, caller — methodist Y, when POST, then 404 `course.not_found` (collapse — нет повідомлення про існування чужого draft).
- [ ] **AC-l3-8 (title too long):** Given title=201 chars, when POST, then 400 `lesson.invalid_payload`.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `CreateLesson(ctx, orgID, userID, courseID uuid.UUID, req CreateCourseLessonRequest) (Lesson, error)`.
- [ ] Step 2 — Service flow:
   1. `checker.IsMethodist(orgID, userID)` → 403 if false.
   2. `coursesRepo.GetByID(orgID, courseID)` → 404 if missing (handles AC-10 cross-org).
   3. If caller != course.CourseOwnerID → 404 (collapse — AC-l3-7).
   4. Domain `NewDraftLesson(courseID, title, sequence, durationSeconds)` → on validation err → 400.
   5. `lessonsRepo.CreateDraft(lesson)` → on `ErrSequenceConflict` → 409.
   6. Return Lesson.
- [ ] Step 3 — Handler `PostCourseLessons(w, r)` — реєструвати path. Extract course_id з URL.
- [ ] Step 4 — Тести: AC-l3-1..AC-l3-8 + golden Lesson shape.

## Edge cases

| Кейс | Поведінка |
|---|---|
| course_id у path — invalid UUID | 400 `validation.invalid_path_param`. |
| duration_seconds=0 (literal 0) | OpenAPI minimum=300 → 400. |
| Sequence=0 explicit | OpenAPI minimum=1 → 400. |
| Caller methodist of org A, but URL points to course in org B (cross-org) | `coursesRepo.GetByID(orgA, courseB.id)` → ErrCourseNotFound → 404. AC-10 satisfied. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] Integration test для AC-l3-4 (паралельні POSTs).
- [ ] OpenAPI Swagger UI показує endpoint.
- [ ] PR linked back to `tasks/L-3-post-course-lessons-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
