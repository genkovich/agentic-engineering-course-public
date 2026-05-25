---
status: Approved
owner: QA
reviewers: [Kyrylo, Backend Lead]
updated_at: "2026-05-14"
feature_size: S
stage: "15"
ticket: INC-841
---

# Test plan — Rate limiting

## Levels

| Level | Scope | Tooling |
|---|---|---|
| Unit | Lua-script через mocked Redis | Go testing |
| Integration | Repo з реальним Redis | testcontainers |
| E2E | Full HTTP flow з Auth + RateLimit + Handler | httptest + testcontainers Redis |
| Load | NFR validation: 14k rpm, p95 ≤ 5ms middleware | k6 |

## AC coverage

| AC | Test(s) | Level |
|---|---|---|
| AC-01 (101-й запит → 429) | `TestRateLimit_ExceedsLimit` | integration + E2E |
| AC-02 (інший user не зачеплений) | `TestRateLimit_IsolatedPerUser` | integration |
| AC-03 (Redis down → fail-open) | `TestRateLimit_RedisTimeout_AllowsRequest` | integration |

## Edge cases / error paths
- Точно 100 запитів у вікні — 100-й має пройти, 101-й — `429`.
- Запити рівно на межі вікна (60s + 1ms) — найстаріший має бути викинутий.
- Concurrent burst (100 паралельних запитів від одного user) — `ZCARD` має бути atomic.
- Redis returns malformed reply — repo returns error, middleware fail-open.

## Test data
- User UUIDs генеруємо в тесті (UUID v7).
- Redis cleanup — `FLUSHDB` між тестами (testcontainers — окремий instance).

## NFR validation
- **Latency p95 ≤ 5ms** → k6 з 1000 VUs, виміри `http_req_duration` тільки на middleware (через test handler без бізнес-логіки).
- **Throughput 14k rpm** → k6 sustained 240rps протягом 5хв; success rate ≥ 99.9%.

## CI
- Unit + integration — на PR.
- Load — nightly + перед release tag.
