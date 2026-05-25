---
id: F-4
epic: course-lesson-mvp
project: BeerLMS
wave: 1
priority: Must
estimate: 0.5d
aggregate: foundation
blocks: [C-5, L-6]
blocked_by: []
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-06]
sad_refs: ["§6 endpoint-level publishLesson", "§6 US-03 publishCourse"]
openapi_paths: []
adr_refs: [ADR-0002]
---

# F-4 · Redis `Idempotency-Key` dedup helper (24h window)

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 1 (foundation)

## Місце в послідовності

- **Блокується:** нічим. Redis client уже у репо.
- **Блокує:** C-5 (`POST /courses/{id}/publish`), L-6 (`POST /lessons/{id}/publish`) — обидва вимагають `Idempotency-Key` header (openapi mandatory).
- **Чому в цій хвилі:** retry-safe publish — core invariant. Без помічника два publish-handler-и продублюють Redis-логіку.

## Why (user story)

As a backend developer, I want a reusable idempotency-key helper `idempotency.CheckOrStore(key, response, ttl)`, so that publish handlers могли deduplicate retry-и протягом 24h (openapi mandate) і не дублювали outbox events на client-side retry storms.

ADR-0002 (Redis as shared infra). PRD AC-06 (publish idempotent — same `published_at` on republish).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-03-publishcourse]] + endpoint-level publishLesson у §6
- 🗄  Data delta:  none — Redis only.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `IdempotencyKeyHeader` parameter (mandatory on publish)
- 📜 Relevant ADR: [[../adr/0002-add-redis-as-shared-infrastructure|ADR-0002]]
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-06

## Data delta

```
NO DB CHANGES.

Redis keys:
  idemp:{namespace}:{idempotency-key}   -- stores serialized response (JSON)
  TTL = 24h (openapi mandate)

Example namespaces:
  publish-course   -- C-5
  publish-lesson   -- L-6
```

## API contract

_No HTTP surface. Internal Go pkg consumed by publish handlers._

```
internal/idempotency/store.go
  type Store interface {
    // CheckOrStore atomically checks for a cached response under key;
    // якщо cached → return (cached, true, nil) — caller responds із cached body.
    // якщо нема → SETNX-ить marker ("PENDING") і returns (nil, false, nil) — caller execute-ить full flow, потім викликає Commit(...).
    CheckOrStore(ctx, namespace, key string, ttl time.Duration) (cached []byte, hit bool, err error)

    // Commit зберігає final response після successful execution.
    Commit(ctx, namespace, key string, response []byte, ttl time.Duration) error

    // Discard видаляє PENDING marker якщо tx failed — щоб retry міг переграти.
    Discard(ctx, namespace, key string) error
  }
```

## Acceptance criteria (GWT)

- [ ] **AC-id-1 (first call — miss):** Given нема key у Redis, when `CheckOrStore("publish-lesson", "K1", 24h)`, then returns `(nil, false, nil)`. У Redis з'являється marker `PENDING` з TTL 24h.
- [ ] **AC-id-2 (Commit зберігає response):** Given marker `PENDING` existing, when `Commit(ns, K1, responseJSON, 24h)`, then у Redis key має JSON value (overwrites `PENDING`); TTL переоновлено.
- [ ] **AC-id-3 (second call — hit cached):** Given Commit-нуто response, when `CheckOrStore(ns, K1, 24h)` called again, then returns `(responseJSON, true, nil)`.
- [ ] **AC-id-4 (second call mid-flight — PENDING):** Given marker `PENDING` existing без Commit-у (попередня call ще виконується), when `CheckOrStore(ns, K1, 24h)` called, then returns `(nil, false, ErrPending)` — caller respond-ить 409 `service.retry_pending`.
- [ ] **AC-id-5 (Discard після failure):** Given PENDING marker, when `Discard(ns, K1)`, then key видалено; наступний `CheckOrStore` — miss.
- [ ] **AC-id-6 (Redis down — fail-close):** Given Redis недоступний, when CheckOrStore called, then returns `(nil, false, err)`. Caller responds 503 `service.unavailable` — fail-close (на відміну від F-3) бо без dedup ризикуємо duplicate outbox event-ом.
- [ ] **AC-id-7 (different namespaces ізольовані):** Given Commit у ns="publish-course" із key="K1", when `CheckOrStore("publish-lesson", "K1", ...)`, then miss — keys не collide.

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити Go pkg `beer-lms-api/internal/idempotency/`. Файли: `store.go` (interface + sentinel errors `ErrPending`), `redis_store.go` (impl), `redis_store_test.go`.
- [ ] Step 2 — У `redis_store.go` реалізувати: CheckOrStore через `SET key "PENDING" NX EX 86400` → якщо OK (`SETNX` success) → return `(nil, false, nil)`; якщо вже існує → GET key → якщо "PENDING" return ErrPending, інакше return value as cached.
- [ ] Step 3 — `Commit` — `SET key <response> EX 86400` (overwrite + refresh TTL).
- [ ] Step 4 — `Discard` — `DEL key`.
- [ ] Step 5 — Юніт-тести через `miniredis` — покрити AC-id-1..AC-id-7.
- [ ] Step 6 — Wire constructor у `cmd/api/main.go`.

## Edge cases

| Кейс | Поведінка |
|---|---|
| PENDING marker stuck (handler crashed без Discard) | TTL 24h гарантує авто-cleanup. У worst case retry waiter блокується на 24h. Документуємо як known limit. |
| Race: дві goroutines одночасно SETNX-ять | Одна win, друга hit PENDING → ErrPending → 409. Caller retry-ить пізніше. |
| Caller передає `key == ""` | Повертаємо `ErrInvalidKey` early (без Redis touch). |
| Response > Redis-овського max value (512 MB) | Не наш case — response типу Lesson < 10 KB. Документувати у docstring що caller має stay reasonable. |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] `go vet` + `golangci-lint run` clean у `internal/idempotency/`.
- [ ] Coverage ≥ 90% у `redis_store.go`.
- [ ] PR linked back to `tasks/F-4-redis-idempotency-helper.md`.
- [ ] `tracker.md` оновлено: status `done`.
