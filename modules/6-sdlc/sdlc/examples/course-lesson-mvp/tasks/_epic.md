---
type: epic
project: BeerLMS
feature: course-lesson-mvp
iteration: 2
created: 2026-05-25
stories_total: 30
stories_done_at_start: 1
waves: 5
scope_note: "Regenerated 2026-05-25 to cover ALL 5 schema-ready aggregates (courses, lessons, lesson_completions, user_preferences, comments) — 18 openapi endpoints. Migrations 000020-000022 already shipped (commit 931deca); MIG-1 is a historic placeholder, not new work."
---

# Epic: course-lesson-mvp (full PRD scope)

**Ітерація:** 2 (regenerated; supersedes iter 1 from 2026-05-24)
**Дата створення:** 2026-05-25

## Проблема

BeerLMS-org-и сьогодні роздають async-навчання через Notion + Slack: lesson-контент живе у Notion-сторінках, оголошення про публікацію — у Slack-нитках, прогрес ніде не агрегується. Це створює фрагментацію для ~80 learner-ів у пілотних org-ах і ~5–10 methodist-ів (PRD §1).

## Рішення

Approach C — Progressive Async Learning + Social Completion (PRD §13 RICE=81). v1 покриває **усі 5 aggregate roots**: methodist створює course → додає lesson із block-based body → публікує → member читає → відмічає completion з privacy toggle → бачить peer-signal → опційно коментує + admin може hide.

**Scope расширення з iter 1:** попередня версія (8 story-ей) покривала тільки `lessons` aggregate. Iter 2 додає `courses`, `lesson_completions`, `user_preferences`, `comments` повністю — `contracts/openapi.yaml v1.1.0` уже містить усі 18 endpoint-ів, і `migrations 000021/000022` уже створюють схеми для всіх 5 aggregate-ів. Розширення йде по контракту.

## Progress

### Wave 1 — Foundation (4 stories, parallel)

- [ ] [[F-1-checkers-is-methodist-is-admin|F-1: IsMethodist + IsAdmin role-check funcs]] — 0.5d — Must
- [ ] [[F-2-outbox-infrastructure|F-2: Outbox infrastructure (migration 000023 + Go pkg)]] — 1d — Must
- [ ] [[F-3-redis-rate-limit-helper|F-3: Redis token-bucket rate-limit helper]] — 0.5d — Must
- [ ] [[F-4-redis-idempotency-helper|F-4: Redis Idempotency-Key dedup helper]] — 0.5d — Must

### Wave 2 — Domain + Repo (4 stories, mostly parallel)

- [ ] [[C-1-domain-course|C-1: Course domain entity + factory]] — 0.5d — Must
- [ ] [[C-2-postgres-course-repo|C-2: PostgresCourseRepository (5 methods) + integration tests]] — 1d — Must
- [ ] [[L-1-domain-lesson-block|L-1: Lesson + LessonBlock domain + factory]] — 1d — Must
- [ ] [[L-2-postgres-lesson-repo|L-2: PostgresLessonRepository (7 methods) + UNIQUE translation]] — 1.5d — Must

### Wave 3 — Handlers (8 stories, parallel within wave)

- [ ] [[C-3-post-courses-handler|C-3: POST /courses (createCourse + rate-limit)]] — 0.75d — Must
- [ ] [[C-4-get-courses-handlers|C-4: GET /courses + GET /courses/{id} (existence-hiding)]] — 0.75d — Must
- [ ] [[C-5-post-courses-publish-handler|C-5: POST /courses/{id}/publish (outbox + idempotency)]] — 1d — Must
- [ ] [[C-6-patch-courses-reorder-handler|C-6: PATCH /courses/{id}/lessons/reorder]] — 0.5d — Must
- [ ] [[L-3-post-course-lessons-handler|L-3: POST /courses/{id}/lessons (createCourseLesson)]] — 0.75d — Must
- [ ] [[L-4-get-lessons-handlers|L-4: GET /lessons + GET /lessons/{id} (no peer-signal)]] — 0.75d — Must
- [ ] [[L-5-post-blocks-handler|L-5: POST /lessons/{id}/blocks (polymorphic payload)]] — 0.5d — Must
- [ ] [[L-6-post-lessons-publish-handler|L-6: POST /lessons/{id}/publish (outbox + idempotency)]] — 1d — Must

### Wave 4 — Completions + Preferences + Comments (10 stories)

- [ ] [[CMP-1-domain-and-repo-completions|CMP-1: LessonCompletion domain + repo + tests]] — 0.5d — Must
- [ ] [[CMP-2-post-completion-handler|CMP-2: POST /lessons/{id}/completion (idempotent via UNIQUE)]] — 0.5d — Must
- [ ] [[CMP-3-peer-blob-aggregation-cache|CMP-3: Peer-blob aggregation + Redis cache (60s TTL)]] — 1d — Must
- [ ] [[CMP-4-extend-get-lesson-with-peer-signal|CMP-4: Extend GET /lessons/{id} із peer_completion field]] — 0.5d — Must
- [ ] [[P-1-domain-and-repo-preferences|P-1: UserPreference + audit domain + repo]] — 0.5d — Must
- [ ] [[P-2-preferences-handlers|P-2: GET/PATCH /me/preferences handlers]] — 0.75d — Must
- [ ] [[CMT-1-domain-and-repo-comments|CMT-1: Comment + CommentAudit domain + repo]] — 0.5d — Must
- [ ] [[CMT-2-post-comment-handler|CMT-2: POST /lessons/{id}/comments (rate-limit + escape)]] — 0.75d — Must
- [ ] [[CMT-3-list-comments-handler|CMT-3: GET /lessons/{id}/comments (cursor + placeholder)]] — 0.5d — Must
- [ ] [[CMT-4-hide-comment-handler|CMT-4: POST /comments/{id}/hide (admin + audit)]] — 0.5d — Must

### Wave 5 — E2E (3 stories, parallel)

- [ ] [[E-1-e2e-course-lesson-lifecycle|E-1: E2E course→lesson lifecycle + cross-org 404]] — 0.5d — Must
- [ ] [[E-2-e2e-peer-signal-and-preferences|E-2: E2E peer-signal + preferences + threshold]] — 0.75d — Must
- [ ] [[E-3-e2e-comments-moderation|E-3: E2E comments + moderation + audit preservation]] — 0.5d — Must

### Historic (already shipped — for traceability, not TODO)

- [x] **MIG-1: Migrations 000020 + 000021 + 000022 (merged у `931deca`)** — schema для всіх 5 aggregate-ів + indexes + `is_methodist` колонки. **Status: done.** No new work; placeholder для coverage matrix.

**Total:** 1/30 done (MIG-1); 29 TODO; ~20 person-days; ~10 calendar days з 2–3 паралельними impl-agents.

## Dependencies

```
Wave 1 (foundation, всі parallel)
F-1 (checkers)   F-2 (outbox)   F-3 (rate-limit)   F-4 (idempotency)
   │                │                │                  │
   └──┬─────────────┼────────────────┼──────────────────┘
      │             │                │
      ▼             │                │
Wave 2 (domain + repo, mostly parallel)
C-1 → C-2          │                │
L-1 → L-2          │                │
   │                │                │
Wave 3 (handlers)   │                │
C-3 ← C-2 + F-3                     │
C-4 ← C-2                           │
C-5 ← C-2, L-2, F-2, F-4            │
C-6 ← C-2, L-2
L-3 ← L-2, C-2
L-4 ← L-2
L-5 ← L-2
L-6 ← L-2, F-2, F-4

Wave 4 (other aggregates)
CMP-1 ← L-2                          ↓
CMP-2 ← CMP-1                        E-2 ← CMP-4, P-2
CMP-3 ← CMP-1, P-1                   E-3 ← CMT-2, CMT-3, CMT-4
CMP-4 ← CMP-3, L-4
P-1   ← F-1
P-2   ← P-1
CMT-1 ← L-2
CMT-2 ← CMT-1, F-3
CMT-3 ← CMT-1
CMT-4 ← CMT-1, F-1

Wave 5 (E2E)
E-1 ← C-3, C-4, C-5, L-3, L-4, L-5, L-6
E-2 ← CMP-4, P-2
E-3 ← CMT-2, CMT-3, CMT-4
```

## Waves

| Wave | Stories | Parallel | Goal |
|------|---------|----------|------|
| 1 | F-1, F-2, F-3, F-4 | yes | Foundation: role-checkers + outbox + Redis helpers |
| 2 | C-1, C-2, L-1, L-2 | yes (across C and L) | Domain + persistence для courses + lessons |
| 3 | C-3, C-4, C-5, C-6, L-3, L-4, L-5, L-6 | yes | 8 handler-ів для courses + lessons endpoints |
| 4 | CMP-1..4, P-1, P-2, CMT-1..4 | yes within sub-chains | Completions + preferences + comments (3 малих aggregates) |
| 5 | E-1, E-2, E-3 | yes | End-to-end verification per aggregate cluster |

## Scope

### Що входить

- **Усі 5 aggregate roots:** `courses` (US-01, US-03, US-05), `lessons` + `lesson_blocks` (US-02, US-04), `lesson_completions` (US-06), `user_preferences` + `user_preference_audit` (US-07, US-08 part), `comments` + `comment_audit` (US-09, US-10).
- **18 endpoints** (всі openapi.yaml v1.1.0 paths): 5 courses + 5 lessons + 2 completion + 3 comments + 2 preferences + reorder.
- **Foundation infra:** outbox events (NEW migration 000023), Redis rate-limit helper, Redis idempotency-dedup helper, IsMethodist+IsAdmin checkers.
- **Outbox events:** `course.published`, `lesson.published`.
- **Privacy/security:** existence-hiding 404 (AC-07, AC-10), HTML-escape comments, anti-fingerprinting threshold `count<3` (AC-15), GDPR-default `private` peer_visibility (AC-13).
- **Rate-limits:** 30 req/min на POST /courses, 10 req/h на POST /comments.
- **Idempotent publish:** Idempotency-Key mandatory + 24h Redis dedup (C-5, L-6).

### Що НЕ входить

- Native video upload (`embed_url` only — PRD §3).
- Edit-after-publish (immutable published у v1).
- Threaded comments / reply-to-reply (flat list у v1).
- Notification fan-out на completion/comment (deferred v2).
- Public profile pages completer-ів.
- Course catalog / full-text search.
- Deprecated `POST /lessons` (top-level, body-based course_id) — NOT included; canonical route `POST /courses/{id}/lessons` через L-3.
- Outbox **consumer** side (Kafka, webhook, notification worker) — only producer + dispatcher stub.

## Ризики

| Ризик | Severity | Mitigation |
|---|---|---|
| Concurrent INSERT із однаковим sequence (lessons / blocks / completions) | Medium | UNIQUE constraints на DB; repo translates `pq.unique_violation` → domain ErrSequenceConflict / ErrCompletionExists. Жодного app-level лока. |
| Cross-org leak через repo bypass | High | Архітектурний інваріант — repo SELECT через JOIN courses(org_id). Integration tests перевіряють "cross-org draft → ErrNotFound" по кожному repo. |
| Outbox dispatch — consumer side outside scope | Low | Event пишеться у tx; dispatcher stub лог-ує і marks dispatched. Consumer migration в v2. |
| Polymorphic block payload — JSON Schema 2020-12 не enforced | Low | additionalProperties=true з documented expected shape per block_type (ADR-0001). Handler-side validation у L-5. |
| Idempotency-Key Redis dedup — Redis SPOF на publish path | Medium | Fail-close: Redis down → 503 (краще запит відмовити ніж дублювати event). F-4 contract. |
| Peer-blob cache TTL 60s може ввести inconsistency | Low | Per PRD §6 NFR + OQ-8 acceptable v1. Future: invalidate-on-write через outbox event. |
| Migration 000023 (outbox) ще не у репо — нова | Medium | F-2 — окрема story із explicit up/down + integration test. Robust enough щоб не блокувати C-5/L-6. |

## Метрики успіху

1. **Methodist adoption** — ≥ 40% активних methodists із ≥ 1 published course (60d, PRD §7).
2. **Published courses count** — ≥ 3 across pilot orgs (30d).
3. **Peer-completion engagement** — ≥ 40% members з ≥ 1 lesson view мають ≥ 1 completion (60d) — Approach C validation.
4. **Public opt-in rate** — ≥ 25% completers opt-in `public` (60d).
5. **Comment engagement** — ≥ 15% published lessons мають ≥ 1 comment (60d).
6. **Read latency p95** — GET /lessons/{id} (з peer-signal) ≤ 400 мс.
7. **Outbox dispatch lag** — < 5s end-to-end (when consumer додається у v2).

## Scope-expansion rationale (vs iter 1)

| Trigger | Result |
|---|---|
| openapi.yaml v1.1.0 уже містить 18 endpoint-ів (всі 5 aggregates) | Iter 1's 8 lesson-only stories — only ⅓ покриття контракту. Регенерація необхідна. |
| migrations 000020-000022 merged 2026-05-24 | Створили схеми для всіх 5 aggregates. Iter 1's S-2 (lessons-only migration) — stale. |
| Outbox у репо відсутній (verified `grep -i outbox`) | Iter 1's S-7 припускав existing outbox — fаlse. F-2 додає infrastructure. |
| Reusable Redis rate-limit + idempotency — повторювалися б у кожному handler-і | F-3 + F-4 — DRY. |

Detail rationale + AC coverage matrix — [[_generation|`_generation.md`]].
