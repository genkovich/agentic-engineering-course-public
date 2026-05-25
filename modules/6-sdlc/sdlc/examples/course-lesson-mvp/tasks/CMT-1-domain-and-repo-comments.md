---
id: CMT-1
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.5d
aggregate: comments
blocks: [CMT-2, CMT-3, CMT-4]
blocked_by: [L-2]
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-16, AC-18]
sad_refs: ["§6 US-09", "§6 US-10"]
openapi_paths: []
adr_refs: []
---

# CMT-1 · `Comment` + `CommentAudit` domain + repo + tests

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 4

## Місце в послідовності

- **Блокується:** L-2 (cross-aggregate fetch parent lesson для org-resolution).
- **Блокує:** CMT-2 (POST), CMT-3 (GET), CMT-4 (hide moderation).
- **Чому в цій хвилі:** domain + repo разом — небагато; 3 handler-и далі залежать від нього.

## Why (user story)

As a backend developer, I want `Comment` + `CommentAudit` types + repo, so that comment lifecycle (create + list + hide) має consistent persistence layer із audit-preserved original content на hide.

PRD US-09 / US-10. AC-16 (post comment), AC-18 (hide preserves original у audit).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-09-createcomment]], [[../sad.md#us-10-hidecomment]]
- 🗄  Data delta:  inherits MIG-1 (`comments` + `comment_audit` у migration 000021)
- 🌐 API contract: [[../contracts/openapi.yaml]] — `Comment`, `CommentListResponse`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-16, AC-18
- 🧬 Parity ref:   mirror `mentorship/infra/session_repo.go` (tx-aware Hide із audit insert)

## Data delta

```
NO DB CHANGES. Shape:

Comment:
  id (UUID v7), lesson_id (UUID), author_id (UUID),
  content (TEXT), status (enum: visible|hidden),
  created_at, updated_at

CommentAudit:
  id (UUID v7), comment_id (UUID), moderator_id (UUID),
  action (enum: hidden), original_content (TEXT), created_at
```

## API contract

_No HTTP._

```go
type Repository interface {
  Insert(ctx, c Comment) (Comment, error)
  GetByID(ctx, id uuid.UUID) (Comment, error)    // does NOT filter by org — handler resolves через lesson
  ListByLesson(ctx, lessonID uuid.UUID, after *uuid.UUID, limit int) ([]Comment, bool, error)
  // Hide: tx — update comment + insert audit + replace content із placeholder.
  Hide(ctx, commentID, moderatorID uuid.UUID, placeholder string) (Comment, error)
}
```

## Acceptance criteria (GWT)

- [ ] **AC-cmt1-1 (factory):** `NewComment(lessonID, authorID, content)` returns Comment з UUID v7, status='visible', timestamps now.
- [ ] **AC-cmt1-2 (Insert happy):** INSERT row returned; status='visible'.
- [ ] **AC-cmt1-3 (Hide tx — AC-18):** Given visible comment, when Hide(commentID, modID, '[hidden by moderator]'), then comment.status='hidden', content=placeholder; audit row created із original_content preserved.
- [ ] **AC-cmt1-4 (Hide idempotent):** Already-hidden → return existing (no new audit row).
- [ ] **AC-cmt1-5 (ListByLesson cursor):** Cursor pagination ordered by created_at DESC (per openapi description).
- [ ] **AC-cmt1-6 (sentinels):** `ErrCommentNotFound`, `ErrCommentAlreadyHidden`, `ErrInvalidPayload` — exported.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/comments/domain/comment.go` + `comment_audit.go` + `errors.go`.
- [ ] Step 2 — Створити `beer-lms-api/internal/modules/comments/ports/repository.go`.
- [ ] Step 3 — Створити `beer-lms-api/internal/modules/comments/infra/postgres_comment_repo.go`. Constructor: `NewPostgresCommentRepository(db *database.DB)`.
- [ ] Step 4 — Реалізувати усі 4 методи. Hide flow: BEGIN; SELECT current; if status=='hidden' return cached; INSERT audit; UPDATE comment; COMMIT.
- [ ] Step 5 — Integration tests testcontainers: AC-cmt1-1..AC-cmt1-6.

## Edge cases

| Кейс | Поведінка |
|---|---|
| `content` довжина > 2000 chars | Repo НЕ валідує — handler-side (AC-17). Repo accept-ить будь-яку довжину. |
| Hide moderator deleted (FK RESTRICT) | Cannot delete user with audit rows — handled by DB. |
| `ListByLesson` із пустого lesson | Returns []Comment{} + has_next=false. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Integration tests; coverage ≥ 85%.
- [ ] `go vet` + `golangci-lint run` clean.
- [ ] PR linked back to `tasks/CMT-1-domain-and-repo-comments.md`.
- [ ] `tracker.md` оновлено: status `done`.
