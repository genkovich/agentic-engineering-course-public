---
id: E-3
epic: course-lesson-mvp
project: BeerLMS
wave: 5
priority: Must
estimate: 0.5d
aggregate: e2e
blocks: []
blocked_by: [CMT-2, CMT-3, CMT-4]
status: todo
context_budget: ~2000 tokens
created: 2026-05-25
prd_refs: [AC-16, AC-17, AC-18]
sad_refs: ["§6 US-09", "§6 US-10"]
openapi_paths: []
adr_refs: []
---

# E-3 · E2E comments lifecycle + moderation (create → list → hide → audit assert)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 5

## Місце в послідовності

- **Блокується:** CMT-2 (POST), CMT-3 (GET list), CMT-4 (hide).
- **Блокує:** нічим.
- **Чому в цій хвилі:** комплексний lifecycle для commenting + moderation.

## Why (user story)

As a release engineer, I want a test що демонструє: member posts comment → list returns it → admin hides → list returns placeholder + audit row preserves original, so that moderation invariants assert-ються.

PRD ACs: AC-16 (post happy), AC-17 (length cap), AC-18 (hide + audit preservation).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-09-createcomment]], [[../sad.md#us-10-hidecomment]]
- 🗄  Data delta:  none.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /lessons/{id}/comments`, `GET /lessons/{id}/comments`, `POST /comments/{id}/hide`
- 📜 Relevant ADR: none
- 📋 PRD ACs:      AC-16, AC-17, AC-18

## Data delta

```
NO new tables. Seeds: 1 org + 1 admin + 1 member + 1 published lesson.
```

## Acceptance criteria (GWT)

- [ ] **AC-e3-1 (post + list — AC-16):** member posts "Hello" → list returns 1 item із content="Hello".
- [ ] **AC-e3-2 (length cap — AC-17):** POST із 2001 chars → 400 `validation.comment_too_long`.
- [ ] **AC-e3-3 (rate-limit — AC-17):** 11-й POST у 1h window → 429 `rate_limited`.
- [ ] **AC-e3-4 (admin hides — AC-18):** admin POST /comments/{c}/hide → 200; GET list returns item із content="[hidden by moderator]"; SQL assert: `SELECT original_content FROM comment_audit WHERE comment_id=c` returns initial "Hello".
- [ ] **AC-e3-5 (non-admin cannot hide):** member POST hide → 403 `comment.not_moderator`.
- [ ] **AC-e3-6 (HTML escape — §6.1.7):** POST content="<script>alert(1)</script>" → GET returns escaped HTML entity content (not raw script).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/test/e2e/comments_moderation_test.go`.
- [ ] Step 2 — Seed: 1 org + 1 admin + 1 member + 1 published lesson із 1 block.
- [ ] Step 3 — Сценарії per AC.
- [ ] Step 4 — Direct SQL assert для audit row (use testcontainer DB connection).

## Edge cases

| Кейс | Поведінка |
|---|---|
| Rate-limit per-user — test uses unique user-id per AC-e3-3 щоб не conflict-ити з AC-e3-1 | OK; separate user. |
| Hidden comment в pagination | Cursor still works; placeholder showed. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] CI green на pre-merge.
- [ ] PR linked back to `tasks/E-3-e2e-comments-moderation.md`.
- [ ] `tracker.md` оновлено: status `done`.
