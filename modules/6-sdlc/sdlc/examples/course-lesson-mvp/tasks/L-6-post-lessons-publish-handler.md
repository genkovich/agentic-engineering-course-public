---
id: L-6
epic: course-lesson-mvp
project: BeerLMS
wave: 3
priority: Must
estimate: 1d
aggregate: lessons
blocks: [E-1]
blocked_by: [L-2, F-2, F-4]
status: todo
context_budget: ~4000 tokens
created: 2026-05-25
prd_refs: []
sad_refs: ["§6 endpoint-level publishLesson"]
openapi_paths: ["POST /lessons/{id}/publish"]
adr_refs: [ADR-0002]
---

# L-6 · `POST /lessons/{id}/publish` handler (publishLesson + outbox + idempotency)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 1d
**Wave:** 3 (handlers)

## Місце в послідовності

- **Блокується:** L-2 (lesson repo + `CountBlocks`), F-2 (outbox), F-4 (idempotency).
- **Блокує:** E-1 (E2E publish flow).
- **Чому в цій хвилі:** mirror of C-5 але для lesson; складніший за L-3/L-5 через outbox+idemp.

## Why (user story)

As a `methodist` (course_owner), I want to publish a lesson атомарно with `lesson.published` outbox event for downstream consumers (search index, notifications), with idempotency on retry, so that publish-action атомарний.

ADR-0002 (Redis as idempotency store). openapi: `Idempotency-Key` mandatory. Cross-methodist → 403 `lesson.forbidden`.

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#endpoint-publish-lesson]] (endpoint-level у §6)
- 🗄  Data delta:  uses `outbox_events` (F-2 migration 000023)
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /lessons/{id}/publish` (`publishLesson`)
- 📜 Relevant ADR: [[../adr/0002-add-redis-as-shared-infrastructure|ADR-0002]]
- 📋 PRD ACs:      mirror AC-06 (idempotent) for lesson-level

## Data delta

```
Write pattern (transactional):
  BEGIN
    blocksCount := CountBlocks(lessonID)  -- L-2 method
    if blocksCount == 0 → ROLLBACK + 409 lesson.no_blocks
    Publish(orgID, lessonID, tx)          -- L-2 method, returns alreadyPublished bool
    if !alreadyPublished → outbox.Append(tx, {type='lesson.published', aggregate_id=lessonID, payload})
  COMMIT

Idempotency: Redis idemp:publish-lesson:{key} (24h, see F-4).
```

## API contract

```
POST /lessons/{id}/publish
  Headers:
    Idempotency-Key: <uuid>   (REQUIRED)
  AuthN: BearerAuth
  AuthZ: caller == course_owner (parent course) — cross-methodist → 403 lesson.forbidden;
         cross-org → 404 lesson.not_found
  Response:
    200 Lesson (published)
    400 lesson.invalid_payload
    401 auth.unauthorized
    403 lesson.forbidden
    404 lesson.not_found
    409 lesson.no_blocks
    409 service.retry_pending
    503 service.unavailable
```

## Acceptance criteria (GWT)

- [ ] **AC-l6-1 (happy publish):** Given draft lesson із ≥1 block, course_owner caller, fresh Idempotency-Key, when POST publish, then 200 + Lesson (status=published, published_at set). 1 outbox row `lesson.published`.
- [ ] **AC-l6-2 (idempotent same key):** Given previous successful publish + same key, when retry within 24h, then 200 + cached body; no second UPDATE, no second outbox row.
- [ ] **AC-l6-3 (idempotent on already-published, fresh key):** Given lesson вже published, fresh key, when POST, then 200 без зміни `published_at`. No new outbox row.
- [ ] **AC-l6-4 (no blocks):** Given lesson із 0 blocks, when POST, then 409 `lesson.no_blocks`.
- [ ] **AC-l6-5 (cross-methodist — 403):** Given lesson's course owned by methodist X, caller — methodist Y (same org), when POST, then 403 `lesson.forbidden`. Чому 403 а не 404 collapse: openapi mandate per sequence-publish-lesson alt-branch — методист уже визначений як methodist у тій же org, ownership distinguishes them. Information leak обмежений ("existing lesson, not yours").
- [ ] **AC-l6-6 (missing Idempotency-Key):** 400 `lesson.invalid_payload`.
- [ ] **AC-l6-7 (cross-org):** 404 `lesson.not_found`.
- [ ] **AC-l6-8 (Redis down):** 503 `service.unavailable` (fail-close).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `PublishLesson(ctx, orgID, userID, lessonID uuid.UUID, idempKey string) (Lesson, error)`.
- [ ] Step 2 — Service flow:
   1. `idemp.CheckOrStore("publish-lesson", idempKey, 24h)` → cached/PENDING/Redis-err handling як C-5.
   2. `lessonsRepo.GetByIDWithBlocks(orgID, lessonID)` → 404 if missing.
   3. Fetch parent course (`coursesRepo.GetByID(orgID, lesson.CourseID)`) — для owner check.
   4. If caller != course.CourseOwnerID → 403 `lesson.forbidden`.
   5. BEGIN tx.
   6. `lessonsRepo.CountBlocks(lessonID)` → 0 → ROLLBACK + 409 `lesson.no_blocks`.
   7. `lessonsRepo.Publish(orgID, lessonID, tx)` → alreadyPublished bool.
   8. If !alreadyPublished → `outbox.Append(tx, Event{type='lesson.published', aggregate='lesson', id=lessonID, payload=lessonJSON})`.
   9. COMMIT.
   10. `idemp.Commit("publish-lesson", idempKey, responseJSON, 24h)`.
- [ ] Step 3 — Handler `PublishLesson(w, r)` — реєструвати path. Extract Idempotency-Key → 400 if empty.
- [ ] Step 4 — On tx fail → `idemp.Discard(...)`.
- [ ] Step 5 — Тести: AC-l6-1..AC-l6-8 + sanity "1 outbox row per successful publish".

## Edge cases

| Кейс | Поведінка |
|---|---|
| Caller is admin (not course_owner) | 403 (admin не власник lesson — only course_owner може publish). Treat як cross-methodist branch. |
| Lesson вже published, but key від іншого user | Redis dedup scope по namespace+key, не по user. Cached response повертається. Документувати як known issue v1. |
| Outbox INSERT fail (schema mismatch) | Tx rollback; 500; idemp.Discard. F-2 schema повинна не fail-ити. |
| Idempotency-Key валідний UUID, але user намагається використати publish-course key | Окремі namespaces (`publish-course` vs `publish-lesson`) — ізольовані. OK. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Integration tests з testcontainers (Postgres + miniredis) — full publish + replay шлях.
- [ ] Один outbox row per successful publish — sanity counter test.
- [ ] OpenAPI Swagger UI показує endpoint із required Idempotency-Key.
- [ ] PR linked back to `tasks/L-6-post-lessons-publish-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
