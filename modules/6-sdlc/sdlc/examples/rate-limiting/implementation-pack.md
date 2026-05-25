---
status: Approved
owner: Kyrylo
reviewers: [Anna, Backend Lead]
updated_at: "2026-05-14"
feature_size: S
stage: "12"
ticket: INC-841
---

# Implementation Pack — Rate limiting

## Goal
Додати per-user rate limit (100 req/min) у API з 429 + Retry-After і fail-open при недоступності Redis.

## Scope
- Новий пакет `middleware/ratelimit`.
- Lua-script для atomic sliding window.
- Конфіг через env vars (`RATE_LIMIT_RPM`, `RATE_LIMIT_WINDOW_SEC`).
- Метрики + structured logs.
- Тести: unit + integration (testcontainers Redis) + E2E.

## Out of scope
- Per-endpoint квоти.
- DB-driven tiers.
- WebSocket.

## Artifacts (read in this order)
1. [SPEC.md](SPEC.md)
2. [architecture-brief.md](architecture-brief.md)
3. [diagrams/c4-container.md](diagrams/c4-container.md)
4. [diagrams/seq-rate-limit.md](diagrams/seq-rate-limit.md)
5. [data-model.md](data-model.md)
6. [api/openapi.yaml](api/openapi.yaml)
7. ADRs: [0007](adr/0007-sliding-window-rate-limit.md), [0008](adr/0008-rate-limit-fail-open.md)

## Hard Rules
1. Не міняй порядок middleware: **Auth → RateLimit → Handler**.
2. Rate limit ключ — `rl:<user_id>` (UUID v7 з токена); ніколи не `rl:<ip>`.
3. Redis-операція робиться **одним Lua EVAL**, не серією команд.
4. Timeout до Redis — 50ms; при timeout — fail-open.
5. Error code — `rate_limit.exceeded` (рівень domain), у HTTP — 429 з `Retry-After`.
6. Metrics: `rate_limit_decisions_total{decision}`, `rate_limit_redis_errors_total`.
7. Не лишай Lua-script inline у Go — окремий файл `internal/middleware/ratelimit/sliding_window.lua`, embed через `//go:embed`.

## Commands
- Test: `make test`
- Lint: `make lint`
- Build: `make build`
- Local stack: `docker compose up -d redis`

## Traceability

| AC | Task | Test | PR | Status |
|---|---|---|---|---|
| AC-01 | T1, T3, T5 | `TestRateLimit_ExceedsLimit` | TBD | Planned |
| AC-02 | T1, T5 | `TestRateLimit_IsolatedPerUser` | TBD | Planned |
| AC-03 | T3, T4, T5 | `TestRateLimit_RedisTimeout_AllowsRequest` | TBD | Planned |

## Open questions
- [ ] (None)

## Sign-off
- [x] PM: Anna, 2026-05-14
- [x] Tech Lead: Kyrylo, 2026-05-14
