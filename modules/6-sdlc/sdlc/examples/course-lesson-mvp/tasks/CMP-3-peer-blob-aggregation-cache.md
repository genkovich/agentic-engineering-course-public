---
id: CMP-3
epic: course-lesson-mvp
project: BeerLMS
wave: 4
priority: Must
estimate: 1d
aggregate: completions
blocks: [CMP-4]
blocked_by: [CMP-1, P-1]
status: todo
context_budget: ~3500 tokens
created: 2026-05-25
prd_refs: [AC-14, AC-15]
sad_refs: ["§6 US-08"]
openapi_paths: []
adr_refs: [ADR-0002]
---

# CMP-3 · Peer-blob aggregation + Redis cache (60s TTL, anti-fingerprint threshold)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 1d
**Wave:** 4

## Місце в послідовності

- **Блокується:** CMP-1 (CountByLesson + RecentPublicByLesson), P-1 (user_preferences read для visibility filter).
- **Блокує:** CMP-4 (`GET /lessons/{id}` extension consumes peer-blob service).
- **Чому в цій хвилі:** heaviest sub-story у completions; cache інфра + privacy threshold — own PR.

## Why (user story)

As a `member`, I want a peer-completion summary (count + up to 5 public recent completers + my_completed flag) for each lesson, cached 60s у Redis to avoid recomputing per request, with anti-fingerprinting threshold `count < 3 → count: null` to protect small-org privacy.

PRD US-08. AC-14 (peer-completion shape), AC-15 (threshold). PRD NFR (peer-blob cache 60s TTL).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-08-peer-completion-signal]]
- 🗄  Data delta:  none — read-only aggregation.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `PeerCompletionSignal`, `PeerCompleter` schemas
- 📜 Relevant ADR: [[../adr/0002-add-redis-as-shared-infrastructure|ADR-0002]] (Redis як cache backend)
- 📋 PRD ACs:      AC-14, AC-15 + OQ-7 (threshold=3 у v1)

## Data delta

```
NO writes. SELECTs на lesson_completions + user_preferences + users (JOIN).
Cache layer: Redis key `peer-blob:{lesson_id}:{org_id}` TTL=60s.
```

## API contract

_No HTTP. Internal Go pkg consumed by CMP-4 handler._

```go
// internal/modules/completions/app/peer_blob_service.go
type PeerBlobService interface {
  GetForLesson(ctx, orgID, userID, lessonID uuid.UUID) (PeerSignal, error)
}

type PeerSignal struct {
  Count            *int                  // nullable (AC-15 threshold)
  RecentCompleters []PeerCompleter       // empty if threshold fires
  MyCompleted      bool
}
```

## Acceptance criteria (GWT)

- [ ] **AC-cmp3-1 (cache miss — fresh compute):** Given 5 completions (3 public, 2 private), when first call, then count=5, recent_completers=3 public ordered desc, my_completed correctly per caller. Redis key set.
- [ ] **AC-cmp3-2 (cache hit):** Given previous call cached, when second call within 60s, then result identical; no DB queries (verify via metrics/mock).
- [ ] **AC-cmp3-3 (cache expiry):** Given 61s passed, when call, then re-compute + new key.
- [ ] **AC-cmp3-4 (threshold fires — AC-15):** Given count=2, when call, then `count=nil, recent_completers=[]`. `my_completed` залишається чесним.
- [ ] **AC-cmp3-5 (threshold edge — count=3):** Given exactly 3 completions, when call, then count=3 returned (≥3 threshold, NOT <3).
- [ ] **AC-cmp3-6 (my_completed always honest):** Given caller has completion, when call, then `my_completed=true` regardless of threshold.
- [ ] **AC-cmp3-7 (different orgs ізольовані у cache):** Cache key includes `{org_id}` — same lesson_id у org A vs B не collide.
- [ ] **AC-cmp3-8 (Redis down — degraded):** Given Redis недоступний, when call, then compute directly from DB; no cache write/read; return signal as normal (fail-open для read path — better than 503).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити `beer-lms-api/internal/modules/completions/app/peer_blob_service.go`.
- [ ] Step 2 — Flow:
   1. Build cache key `peer-blob:{lesson_id}:{org_id}`.
   2. `GET key` з Redis → if hit → deserialize → augment `my_completed` per-caller (compute separately so caller-A-cached доступне для caller-B із own my_completed flag) → return.
   3. Cache miss: `completionsRepo.CountByLesson(lessonID, orgID)`. If count < 3 → `count=nil, recent=[]`.
   4. If count >= 3 → `completionsRepo.RecentPublicByLesson(lessonID, orgID, 5)` → map to []PeerCompleter.
   5. `completionsRepo.GetByUserLesson(callerID, lessonID)` (or cheaper lookup) → my_completed bool.
   6. Serialize {count, recent} (NOT my_completed) → SET key TTL 60s.
   7. Return signal із my_completed plumbed-in.
- [ ] Step 3 — Important: cache контент НЕ включає my_completed бо per-caller. Caching shape має бути aggregate-only.
- [ ] Step 4 — Юніт-тести через mocked repo + miniredis: AC-cmp3-1..AC-cmp3-8.
- [ ] Step 5 — Integration test (testcontainers + miniredis) для AC-cmp3-1, AC-cmp3-5.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Cache invalidation on new completion | NOT у v1 — TTL-only (60s staleness acceptable per PRD §6 NFR + OQ-8). Document як known. |
| Public completer has no `display_name` (legacy users) | JOIN excludes them OR returns empty string — TBD з team. Default: include з empty string, FE renders "Anonymous". |
| `RecentPublicByLesson` returns 5 але <5 actually public | OK — return what we have. |
| Caller in two orgs — call із different orgID context | Cache keyed by org → ізольовані per-org. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] Service + cache tests; coverage ≥ 85%.
- [ ] Integration test з miniredis demonstrating cache hit/miss.
- [ ] PR linked back to `tasks/CMP-3-peer-blob-aggregation-cache.md`.
- [ ] `tracker.md` оновлено: status `done`.
