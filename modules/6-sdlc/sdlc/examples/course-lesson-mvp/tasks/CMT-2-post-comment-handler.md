---
id: CMT-2
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 0.75d
aggregate: comments
blocks: [E-3]
blocked_by: [CMT-1, F-3]
status: todo
context_budget: ~3000 tokens
created: 2026-05-25
prd_refs: [AC-16, AC-17]
sad_refs: ["§6 US-09"]
openapi_paths: ["POST /lessons/{id}/comments"]
adr_refs: []
---

# CMT-2 · `POST /lessons/{id}/comments` handler (rate-limit + HTML-escape)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.75d
**Wave:** 4

## Місце в послідовності

- **Блокується:** CMT-1 (repo), F-3 (rate-limit).
- **Блокує:** E-3 (E2E comments lifecycle).
- **Чому в цій хвилі:** окремий PR з rate-limit + sanitization.

## Why (user story)

As a `member`, I want to post a plain-text comment on a published lesson with server-side HTML-escape and rate-limit 10 comments/h/user, so that XSS + spam захищені.

PRD US-09. AC-16 (happy), AC-17 (length + rate-limit). §6.1 abuse-case 7 (XSS escape).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-09-createcomment]]
- 🗄  Data delta:  INSERT into `comments` (MIG-1).
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /lessons/{id}/comments` (`createComment`), `CreateCommentRequest`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-16, AC-17 + §6.1 abuse cases 7, 8

## Data delta

```
INSERT-only. Content HTML-escaped перед persist (e.g., html.EscapeString).
```

## API contract

```
POST /lessons/{id}/comments
  AuthN: BearerAuth
  AuthZ: orgmw + lesson.status==published AND lesson.org==caller.org
  Rate-limit: 10 req/h/user (F-3 namespace="comments-create")
  Body: CreateCommentRequest {content, maxLength=2000}
  Response:
    201 Comment
    400 validation.comment_too_long
    401 auth.unauthorized
    404 lesson.not_found
    429 rate_limited
```

## Acceptance criteria (GWT)

- [ ] **AC-cmt2-1 (happy — AC-16):** Given valid body (content=20 chars), published lesson same org, when POST, then 201 + Comment {status:'visible'}.
- [ ] **AC-cmt2-2 (content too long — AC-17):** content=2001 chars → 400 `validation.comment_too_long`.
- [ ] **AC-cmt2-3 (HTML escape — §6.1.7):** content="<script>alert(1)</script>", when POST, then DB stores escaped "&lt;script&gt;alert(1)&lt;/script&gt;". Response повертає escaped content.
- [ ] **AC-cmt2-4 (rate-limit — AC-17):** 10 successful POSTs у 1h window, then 11th → 429 `rate_limited`.
- [ ] **AC-cmt2-5 (draft lesson):** 404 `lesson.not_found`.
- [ ] **AC-cmt2-6 (cross-org lesson):** 404.
- [ ] **AC-cmt2-7 (empty content):** content="" → 400 `validation.invalid_payload` (require non-empty).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `CreateComment(ctx, orgID, userID, lessonID, content string) (Comment, error)`.
- [ ] Step 2 — Flow:
   1. `ratelimit.Check("comments-create", userID, 10, 1*time.Hour)` → 429 if exceeded.
   2. `lessonsRepo.GetByIDWithBlocks(orgID, lessonID)` → 404 if missing.
   3. If lesson.status != published → 404 (collapse).
   4. Validate len(content) ∈ (0, 2000] → 400 if not.
   5. Sanitize: `escaped := html.EscapeString(content)`.
   6. Domain `NewComment(lessonID, userID, escaped)`.
   7. `commentsRepo.Insert(c)` → return.
- [ ] Step 3 — Handler `PostLessonComment(w, r)` — реєструвати path.
- [ ] Step 4 — Тести: AC-cmt2-1..AC-cmt2-7.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Content із Unicode emoji | Зберігається (UTF-8 OK у TEXT column); not escaped. |
| Content із newlines | Дозволяємо (FE renders as plain text); not converting to `<br>`. |
| `html.EscapeString` побічно escape-ить `&` у `&amp;` | OK — повертаємо escaped, FE рендерить без re-escape. |
| Rate-limit fail-open | Continue + warning log (F-3 contract). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Handler + service tests; coverage ≥ 80%.
- [ ] OpenAPI Swagger UI показує endpoint.
- [ ] PR linked back to `tasks/CMT-2-post-comment-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
