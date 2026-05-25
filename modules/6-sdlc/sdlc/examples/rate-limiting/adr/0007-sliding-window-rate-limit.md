---
status: Accepted
owner: Kyrylo
reviewers: [Backend Lead]
updated_at: "2026-05-14"
feature_size: S
stage: "11"
ticket: INC-841
---

# 0007 — Use sliding window log in Redis for rate limiting

- **Status:** Accepted
- **Date:** 2026-05-14
- **Deciders:** Kyrylo (Tech Lead), Backend Lead

## Context
Поточний rate limit per-IP, in-memory у API. Heavy users ламають shared limit (інциденти INC-841/842/849). Контракт з Acme Corp вимагає чесний per-user SLA: «100 req/min».

## Decision drivers
- AC-01: точність «100 req/min» — не наближення.
- Latency p95 middleware ≤ 5ms.
- Shared state між API replicas.
- Запобігання SPOF — fail-open при недоступності Redis.

## Considered options
1. **Token bucket у Redis** — простий, дешевий, але approximation; burst-behavior складно пояснити SLA.
2. **Sliding window log у Redis** — точно, fair, легко пояснити; ~1MB total memory.
3. **In-memory per-replica з gossip** — без Redis, але потребує синхронізацію між replicas і непередбачуваний при scale-out.

## Decision outcome
**Chosen: Option 2 — sliding window log у Redis.**
Причина: AC вимагає точність, memory cost мізерний (~1MB), Redis вже є у стеку. Реалізація — atomic Lua script (`ZREMRANGEBYSCORE` + `ZCARD` + умовний `ZADD`).

## Consequences

**Positive**
- Чітке відповідання `100 req/min` — клієнти бачать справедливість.
- Atomic — без гонок.
- TTL = window, авточистка.

**Negative**
- Залежимо від Redis cluster — потрібен fail-open (див. ADR-0008).
- При peak burst — один Lua-eval на запит (~1-2ms додатково).

**Neutral**
- Memory ~1MB — навіть на peak insignificant.

## Links
- SPEC: [SPEC.md](../SPEC.md)
- Related: [ADR-0008 fail-open](0008-rate-limit-fail-open.md)
