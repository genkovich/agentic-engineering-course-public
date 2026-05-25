---
id: F-3
epic: course-lesson-mvp
project: BeerLMS
wave: 1
priority: Must
estimate: 0.5d
aggregate: foundation
blocks: [C-3, CMT-2]
blocked_by: []
status: todo
context_budget: ~2500 tokens
created: 2026-05-25
prd_refs: [AC-17]
sad_refs: ["§6.1 abuse case 4", "§6.1 abuse case 8"]
openapi_paths: []
adr_refs: [ADR-0002]
---

# F-3 · Redis token-bucket rate-limit helper

**Epic:** [[_epic|course-lesson-mvp]]
**Priority:** Must
**Estimate:** 0.5d
**Wave:** 1 (foundation)

## Місце в послідовності

- **Блокується:** нічим. Redis у репо вже є (ADR-0002 prior, mentorship-овський client wiring).
- **Блокує:** C-3 (`POST /courses` — 30 req/min/user), CMT-2 (`POST /lessons/{id}/comments` — 10 comments/h/user).
- **Чому в цій хвилі:** два write-endpoint-и потребують rate-limit; уникнути двох inline-Redis-копій → reusable helper.

## Why (user story)

As a backend developer, I want a reusable token-bucket rate-limit helper `ratelimit.Check(key, limit, window) → (allowed, retryAfter)`, so that handlers `POST /courses` і `POST /lessons/{id}/comments` (та майбутні write-endpoint-и) використовують єдиний патерн і не дублюють Redis INCR + TTL код.

PRD §6.1 abuse-case 4 (course flood), abuse-case 8 (comment spam). AC-17 (`rate_limited` error code).

## Linked artifacts (read-only references — DO NOT inline)

- 🌐 Sequence:    [[../sad.md#us-09-createcomment]] (rate-limit step inlined)
- 🗄  Data delta:  none — Redis only.
- 🌐 API contract: [[../contracts/openapi.yaml]] — `RateLimited` response (429)
- 📜 Relevant ADR: [[../adr/0002-add-redis-as-shared-infrastructure|ADR-0002]]
- 📋 PRD ACs:      [[../PRD.md#5-acceptance-criteria|PRD §5]] — AC-17

## Data delta

```
NO DB CHANGES.

Redis keys:
  ratelimit:{namespace}:{user_id}   -- counter integer
  TTL = window (sliding-window-ish via fixed-window TTL reset)

Example keys у v1:
  ratelimit:courses-create:{uuid}   -- limit=30, window=60s
  ratelimit:comments-create:{uuid}  -- limit=10, window=3600s
```

## API contract

_No HTTP surface. Internal Go pkg consumed by handlers._

```
internal/ratelimit/limiter.go
  type Limiter interface {
    Check(ctx, namespace, identity string, limit int, window time.Duration) (allowed bool, retryAfter time.Duration, err error)
  }

internal/ratelimit/redis_limiter.go
  func (l *RedisLimiter) Check(...) {
    key := "ratelimit:" + ns + ":" + identity
    cnt, _ := INCR(key)
    if cnt == 1 { EXPIRE(key, window) }
    if cnt > limit { ttl := TTL(key); return false, ttl, nil }
    return true, 0, nil
  }
```

## Acceptance criteria (GWT)

- [ ] **AC-rl-1 (within limit):** Given user робить 5 calls із limit=30/min, when `Check("courses-create", uid, 30, 1min)` викликається 5 разів, then всі returns `(true, 0, nil)`.
- [ ] **AC-rl-2 (limit exceeded):** Given 30 successful calls у вікні, when 31-й виклик, then returns `(false, <retryAfter ≤ 1min>, nil)`.
- [ ] **AC-rl-3 (window reset):** Given limit reached, when TTL expires, then наступний call returns `(true, 0, nil)`.
- [ ] **AC-rl-4 (isolated namespaces):** Given user hits courses-limit, when same user calls comments-namespace, then comments counter не зачеплено (різні keys).
- [ ] **AC-rl-5 (isolated users):** Given user A hits limit, when user B calls same namespace, then B not blocked.
- [ ] **AC-rl-6 (Redis down — fail-open):** Given Redis недоступний, when Check called, then returns `(true, 0, err)` із err set. Caller logs but allows request — НЕ блокувати трафік на infra проблему (decision: fail-open для rate-limit; fail-close для idempotency у F-4).

## Checklist (atomic steps for impl-agent)

- [ ] Step 1 — Створити Go pkg `beer-lms-api/internal/ratelimit/`. Файли: `limiter.go` (interface), `redis_limiter.go` (impl), `redis_limiter_test.go`.
- [ ] Step 2 — У `redis_limiter.go` реалізувати `Check` через `INCR` + `EXPIRE` (atomic Lua optional; для v1 ok із двох команд оскільки race condition хіба що sets TTL пізніше — sliding-window-ish ще нормально для anti-spam).
- [ ] Step 3 — Юніт-тести через `miniredis` — покрити AC-rl-1..AC-rl-6.
- [ ] Step 4 — Wire constructor у `cmd/api/main.go` — один `*RedisLimiter` для всіх handler-ів.

## Edge cases

| Кейс | Поведінка |
|---|---|
| Перший INCR returns 1 але EXPIRE падає | На наступному виклику INCR → 2, key без TTL → ніколи не reset. Mitigation: monitoring alert на keys без TTL у Redis (Prometheus metric). Acceptable risk для v1. |
| Limit = 0 (config error) | Перший виклик повертає `(false, 0, nil)` — все блокується. Caller має validate config. |
| Window < 1s | Округлюється Redis-ом до 1s (EXPIRE granularity). Документуємо у docstring. |
| Identity contains `:` | Має escape-итися або просто санітайз перед використанням як key suffix. Для UUID — безпечно (UUID нема `:`). |

## Definition of Done

- [ ] Усі checklist steps зроблені, всі AC зелені.
- [ ] `go vet` + `golangci-lint run` clean у `internal/ratelimit/`.
- [ ] Coverage ≥ 90% у `redis_limiter.go`.
- [ ] PR linked back to `tasks/F-3-redis-rate-limit-helper.md`.
- [ ] `tracker.md` оновлено: status `done`.
