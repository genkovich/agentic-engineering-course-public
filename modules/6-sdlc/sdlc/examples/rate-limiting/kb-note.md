---
status: shipped
owner: Kyrylo
reviewers: [Anna, Backend Lead]
updated_at: "2026-05-20"
feature_size: S
stage: "18"
ticket: INC-841
tags: [api, middleware, rate-limit, kb]
shipped_at: 2026-05-20
---

# Rate limiting per user — KB note

## Summary
Додано per-user rate limit (100 req/min) у API. Алгоритм — sliding window log у Redis через atomic Lua. Fail-open при недоступності Redis + alert у Grafana. Замінив попередній per-IP rate limit, який блокував сусідів через одного heavy-user.

## Links
- SPEC: [[rate-limiting-SPEC]]
- ADRs: [[0007-sliding-window-rate-limit]], [[0008-rate-limit-fail-open]]
- C4: [[rate-limiting-c4-container]]
- Sequence: [[seq-rate-limit]]

## Decisions (highlights)
- **Sliding window log замість token bucket** → ADR-0007. Точність важливіша за дешевизну, memory cost мізерний.
- **Fail-open + alert** → ADR-0008. API availability вища пріоритет, ніж rate limit accuracy.
- **Один Lua EVAL** замість серії Redis-команд — atomicity без зайвих RTT.

## Diagrams
![[rate-limiting-c4-container]]

## Lessons learned
- **Що спрацювало**: Sliding window log виявився легко testable — testcontainers Redis робить інтеграційні тести швидкими.
- **Що б зробили інакше**: Конфіг через env vars був S, але одразу два tier-ліміти (free / paid) попросять у фазі 2 — треба буде винести в DB-driven config. Краще б одразу думали про це у архітектурі.
- **Surprise**: k6 з 1000 VUs виявив, що Lua-script повертав `nil` під рідкою race-умовою (зник на тестах нижчого rps). Виправили `if redis.call(...) == false then ... end` у Lua.

## Related
- [[per-endpoint-quotas]] (планова фаза 2)
- [[redis-cluster-runbook]]
