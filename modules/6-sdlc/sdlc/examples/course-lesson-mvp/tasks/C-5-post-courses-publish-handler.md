---
id: C-5
epic: course-lesson-mvp
project: BeerLMS
wave: 3
priority: Must
estimate: 1d
aggregate: courses
blocks: [E-1]
blocked_by: [C-2, L-2, F-2, F-4]
status: todo
context_budget: ~4000 tokens
created: 2026-05-25
prd_refs: [AC-05, AC-06]
sad_refs: ["§6 US-03"]
openapi_paths: ["POST /courses/{id}/publish"]
adr_refs: [ADR-0002]
---

# C-5 · `POST /courses/{id}/publish` handler (publishCourse + outbox + idempotency)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 1d
**Wave:** 3 (handlers)

## Місце в послідовності

- **Блокується:** C-2 (course repo), L-2 (CountPublishedLessons cross-aggregate guard), F-2 (outbox), F-4 (idempotency).
- **Блокує:** E-1 (E2E publish-flow).
- **Чому в цій хвилі:** найскладніший handler (gate + outbox + dedup) — own story.

## Why (user story)

As a `methodist`, I want to publish my course atomically with a `course.published` outbox event (для downstream notifications, search-index), with idempotency on retry, so that publish-action атомарний і не дублює event-и при client-side retry storms.

PRD US-03. AC-05 (publish gate: ≥1 published lesson required), AC-06 (idempotent — second publish зберігає `published_at`).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-03-publishcourse]]
- 🗄  Data delta:  uses `outbox_events` table (F-2 migration 000023)
- 🌐 API contract: [[../contracts/openapi.yaml]] — `POST /courses/{id}/publish` (`publishCourse`)
- 📜 Relevant ADR: [[../adr/0002-add-redis-as-shared-infrastructure|ADR-0002]] (Redis для Idempotency-Key)
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-05, AC-06

## Data delta

```
NO new tables (outbox у F-2).

Write pattern (transactional):
  BEGIN
    publishedLessonCount := CountPublishedLessons(courseID)  -- L-2 method
    if publishedLessonCount == 0 → ROLLBACK, return 409 course.no_published_lessons
    UPDATE courses SET status='published', published_at=now()
      WHERE id=$1 AND org_id=$2 AND status='draft'
      RETURNING *   (C-2.Publish)
    if alreadyPublished → no UPDATE, return existing course + skip outbox INSERT
    INSERT INTO outbox_events (id, 'course', courseID, 'course.published', payload, now())  (F-2.Append)
  COMMIT

Idempotency-Key dedup (Redis, before BEGIN):
  idemp.CheckOrStore("publish-course", key, 24h)
  if hit → respond cached
  if PENDING → 409 service.retry_pending
  else proceed, then idemp.Commit(...)
```

## API contract

```
POST /courses/{id}/publish
  Headers:
    Idempotency-Key: <uuid>   (REQUIRED — openapi mandatory)
  AuthN: BearerAuth
  AuthZ: caller == course_owner (US-03 — only owner може publish; non-owner → 404 existence-hiding)
  Response:
    200 Course (published)              (success або idempotent re-publish AC-06)
    400 course.invalid_payload          (Idempotency-Key missing/malformed)
    401 auth.unauthorized
    404 course.not_found                (cross-org, non-owner, missing)
    409 course.no_published_lessons     (AC-05 gate)
    409 service.retry_pending           (PENDING marker hit)
    503 service.unavailable             (Redis down — fail-close)
```

## Acceptance criteria (GWT)

- [ ] **AC-c5-1 (happy publish):** Given draft course із 1 published lesson, owner caller, fresh Idempotency-Key, when POST publish, then 200 + Course (status=published, published_at set); 1 row у outbox `course.published`.
- [ ] **AC-c5-2 (gate — AC-05):** Given course з 0 published lessons (drafts OK), when POST publish, then 409 `course.no_published_lessons`. No UPDATE, no outbox row.
- [ ] **AC-c5-3 (idempotent same key — AC-06):** Given previous successful publish + same key, when retry within 24h, then 200 + same response cached; no second UPDATE, no second outbox row; Redis hit.
- [ ] **AC-c5-4 (idempotent on already-published, fresh key — AC-06):** Given course вже published, fresh Idempotency-Key, when POST publish, then 200 без зміни `published_at`. No outbox row (alreadyPublished branch).
- [ ] **AC-c5-5 (missing Idempotency-Key):** Given no header, when POST, then 400 `course.invalid_payload`.
- [ ] **AC-c5-6 (non-owner — collapse to 404):** Given caller ≠ course_owner (could be admin or другий methodist), when POST, then 404 `course.not_found`.
- [ ] **AC-c5-7 (cross-org):** Given course у org Y, caller у org X, when POST, then 404.
- [ ] **AC-c5-8 (Redis down):** Given Redis недоступний, when POST, then 503 `service.unavailable` (fail-close — see F-4 AC-id-6).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — App service `PublishCourse(ctx, orgID, userID, courseID uuid.UUID, idempKey string) (Course, error)`.
- [ ] Step 2 — Service flow:
   1. `idemp.CheckOrStore("publish-course", idempKey, 24h)` → on cached return cached Course; on ErrPending → 409 service.retry_pending; on Redis err → 503.
   2. `repo.GetByID(orgID, courseID)` → 404 if not found.
   3. If caller != course.CourseOwnerID → 404 (collapse).
   4. `BEGIN tx`.
   5. `lessons.repo.CountPublishedLessons(courseID)` → 0 → ROLLBACK + 409 `course.no_published_lessons`.
   6. `courses.repo.Publish(orgID, courseID, tx)` → returns Course + alreadyPublished bool.
   7. If !alreadyPublished → build payload (Course JSON) + `outbox.Append(tx, Event{aggregate_type='course', aggregate_id=courseID, event_type='course.published', payload})`.
   8. `COMMIT tx`.
   9. `idemp.Commit("publish-course", idempKey, responseJSON, 24h)`.
   10. Return Course.
- [ ] Step 3 — Handler `PublishCourse(w, r)` — реєструвати path. Extract Idempotency-Key header → 400 if empty/malformed.
- [ ] Step 4 — On tx failure → `idemp.Discard(...)` щоб retry міг переграти.
- [ ] Step 5 — Handler tests + service tests із testcontainers + miniredis: AC-c5-1..AC-c5-8 + перевірка "1 outbox row per successful publish".

## Edge cases

| Кейс | Поведінка |
|---|---|
| Idempotency-Key — same key, different course | Redis key включає namespace `publish-course:{key}`, але caller може повторно використати key на іншій URI. Це bug на client. Treat as cached response — повертає попередній course. Документувати як known limit; v2 додає bind до URI path. |
| Course із 1 published lesson і lesson got unpublished mid-flight | Race — CountPublishedLessons може бути 0 to 1 to 0. У worst case publish OK при кратной 1 → потім lesson unpublish — course лишається published із 0 lessons. Acceptable: unpublish API не у v1; ризик low. |
| Tx fail після Publish але до outbox.Append | Cancellation — tx rollback автоматично; lesson лишається draft. Discard idempotency marker. Retry OK. |
| Outbox INSERT fail (схема mismatch) | Tx rollback; status revert; 500 generic. F-2 schema повинна не fail-ити в normal operation. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Integration tests із testcontainers (Postgres + miniredis) покривають full publish + replay шлях.
- [ ] Один outbox row per successful publish — sanity counter test.
- [ ] OpenAPI Swagger UI показує endpoint із required Idempotency-Key.
- [ ] PR linked back to `tasks/C-5-post-courses-publish-handler.md`.
- [ ] `tracker.md` оновлено: status `done`.
