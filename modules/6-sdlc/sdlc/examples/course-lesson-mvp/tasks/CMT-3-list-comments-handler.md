---
id: CMT-3
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.5d
aggregate: comments
blocks: [E-3]
blocked_by: [CMT-1]
status: todo
context_budget: ~2000 tokens
created: 2026-05-25
prd_refs: []
sad_refs: ["§6 US-09"]
openapi_paths: ["GET /lessons/{id}/comments"]
adr_refs: []
---

# CMT-3 · `GET /lessons/{id}/comments` handler (cursor, hidden→placeholder)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 4

## Місце в послідовності

- **Блокується:** CMT-1 (repo).
- **Блокує:** E-3.
- **Чому в цій хвилі:** simple list endpoint.

## Why (user story)

As a `member`, I want to see comments on a published lesson, including hidden ones with placeholder content so moderation breadcrumbs visible, so that user досить контексту і trust signal.

PRD US-09 derived from openapi description.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-09-createcomment]]
- 🗄  Data delta:  none — read-only.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `GET /lessons/{id}/comments` (`listLessonComments`), `CommentListResponse`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      US-09 derived

## Data delta

```
NO writes. SELECT з cursor pagination.
```

## API contract

```
GET /lessons/{id}/comments?after=<uuid>&limit=<n>
  AuthN: BearerAuth
  AuthZ: orgmw + lesson.status==published AND lesson.org==caller.org
  Response:
    200 CommentListResponse  (items ordered created_at DESC; hidden returns placeholder content)
    401 auth.unauthorized
    404 lesson.not_found
```

## Acceptance criteria (GWT)

- [ ] **AC-cmt3-1 (list happy):** Given 5 visible comments, when GET, then 200 + 5 items DESC by created_at.
- [ ] **AC-cmt3-2 (hidden returns placeholder):** Given comment status='hidden' із content stored як placeholder `"[hidden by moderator]"` (after CMT-4 hide flow), when GET, then item.content = `"[hidden by moderator]"`. Original content НЕ leak-ається.
- [ ] **AC-cmt3-3 (cursor pagination):** limit=10 + 25 comments → first page 10 + has_next=true; after=last10 → next 10.
- [ ] **AC-cmt3-4 (draft lesson):** 404.
- [ ] **AC-cmt3-5 (cross-org):** 404.
- [ ] **AC-cmt3-6 (default limit):** limit not provided → defaults to 20.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `ListComments(ctx, orgID, userID, lessonID, after *uuid.UUID, limit int) ([]Comment, bool, error)`.
- [ ] Step 2 — Flow:
   1. `lessonsRepo.GetByIDWithBlocks(orgID, lessonID)` → 404 if missing.
   2. If lesson.status != published → 404.
   3. `commentsRepo.ListByLesson(lessonID, after, limit+1)` → return items + has_next.
- [ ] Step 3 — Handler `GetLessonComments(w, r)`. Limit clamp [1, 100] default 20.
- [ ] Step 4 — Тести: AC-cmt3-1..AC-cmt3-6.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Comment created → hidden mid-pagination | Cursor still works; hidden returns placeholder. |
| Cursor — invalid UUID | 400 `validation.invalid_cursor`. |
| 0 comments | 200 + `{items:[], has_next:false}`. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] OpenAPI Swagger UI показує endpoint.
- [ ] PR linked back to `tasks/CMT-3-list-comments-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
