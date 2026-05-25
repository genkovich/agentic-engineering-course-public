---
id: CMT-4
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.5d
aggregate: comments
blocks: [E-3]
blocked_by: [CMT-1, F-1]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-18]
sad_refs: ["§6 US-10"]
openapi_paths: ["POST /comments/{id}/hide"]
adr_refs: []
---

# CMT-4 · `POST /comments/{id}/hide` handler (admin moderation + audit log)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 4

## Місце в послідовності

- **Блокується:** CMT-1 (repo), F-1 (IsAdmin checker).
- **Блокує:** E-3 (E2E moderation flow).
- **Чому в цій хвилі:** simple handler з admin gate + audit.

## Why (user story)

As an `admin`, I want to hide an inappropriate comment (with original content preserved у audit for compliance recall), so that org-discussion clean без втрати traceability.

PRD US-10. AC-18.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-10-hidecomment]]
- 🗄  Data delta:  UPDATE `comments` + INSERT `comment_audit` in tx (MIG-1).
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /comments/{id}/hide` (`hideComment`)
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-18

## Data delta

```
BEGIN
  SELECT comment + parent lesson (для org-resolution).
  if cross-org → ROLLBACK + 404 comment.not_found
  if !IsAdmin → 403
  if status=='hidden' → return existing (idempotent)
  INSERT comment_audit(comment_id, moderator_id, action='hidden', original_content)
  UPDATE comments SET status='hidden', content='[hidden by moderator]', updated_at=now() WHERE id=$1
COMMIT
```

## API contract

```
POST /comments/{id}/hide
  AuthN: BearerAuth
  AuthZ: IsAdmin(orgID, callerID) on org owning the comment's lesson
  Response:
    200 Comment  (status='hidden', content=placeholder)
    401 auth.unauthorized
    403 comment.not_moderator
    404 comment.not_found
```

## Acceptance criteria (GWT)

- [ ] **AC-cmt4-1 (admin hides — AC-18):** Given visible comment same org, admin caller, when POST hide, then 200 + Comment {status:'hidden', content:'[hidden by moderator]'}; DB: status='hidden', content=placeholder; audit row created із original content preserved.
- [ ] **AC-cmt4-2 (non-admin):** Given regular member caller (not admin), when POST hide, then 403 `comment.not_moderator`.
- [ ] **AC-cmt4-3 (cross-org):** Given comment у org Y, admin у org X, when POST hide, then 404 `comment.not_found`.
- [ ] **AC-cmt4-4 (already hidden idempotent):** Given hidden comment, when POST hide again, then 200 + same hidden Comment; no new audit row.
- [ ] **AC-cmt4-5 (missing comment):** 404.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `HideComment(ctx, orgID, moderatorID, commentID uuid.UUID) (Comment, error)`.
- [ ] Step 2 — Flow:
   1. `commentsRepo.GetByID(commentID)` → 404 if missing.
   2. Fetch parent lesson + course для org-resolution.
   3. If lesson.org != orgID → 404 (cross-org).
   4. `checker.IsAdmin(orgID, moderatorID)` → 403 if false.
   5. `commentsRepo.Hide(commentID, moderatorID, "[hidden by moderator]")` — tx з audit.
   6. Return updated Comment.
- [ ] Step 3 — Handler `PostHideComment(w, r)`.
- [ ] Step 4 — Тести: AC-cmt4-1..AC-cmt4-5.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Audit insert fail (FK?) | Tx rollback; comment status НЕ змінено. 500 generic. |
| Moderator deleted FK RESTRICT | Якщо moderator пробує hide після власного видалення — не може (FK enforcement). |
| Comment author == moderator | OK — admin може hide власний comment. |
| Placeholder string потрібно змінити майбутнім | OQ для product; обираємо hardcoded literal `"[hidden by moderator]"` per openapi. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] Integration test: audit row preservation після hide (verify через SELECT comment_audit).
- [ ] OpenAPI Swagger UI показує endpoint.
- [ ] PR linked back to `tasks/CMT-4-hide-comment-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
