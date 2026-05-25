---
status: Accepted
owner: Kyrylo
reviewers: [Backend Lead, SRE]
updated_at: "2026-05-14"
feature_size: S
stage: "11"
ticket: INC-841
---

# 0008 — Rate limit fails open when Redis is unavailable

- **Status:** Accepted
- **Date:** 2026-05-14
- **Deciders:** Kyrylo, Backend Lead, SRE

## Context
Якщо Redis cluster недоступний (timeout > 50ms або connection refused), middleware має або пропустити запит (fail-open), або заблокувати (fail-closed). Це впливає на user-facing SLA.

## Decision drivers
- API availability SLA вища за пріоритет, ніж rate limit accuracy.
- Redis cluster має 99.95% SLA — інциденти рідкі.
- SRE команда хоче alert при fail-open, але не хоче блокувати юзерів.

## Considered options
1. **Fail-open + alert** — пропускаємо запит, інкрементуємо метрику, alerting за threshold.
2. **Fail-closed** — повертаємо `503`, поки Redis не оживе.
3. **Local fallback (per-replica in-memory)** — швидкий, але втрачає shared state і ускладнює тестування.

## Decision outcome
**Chosen: Option 1 — fail-open + alert.**
Причина: rate limit — захист від abuse, а не критичний контракт. Втратити 1 хвилину фільтрації під час Redis-інциденту краще, ніж відмовити всім користувачам.

## Consequences

**Positive**
- API availability не залежить від Redis.
- SRE отримує сигнал на справжній інцидент.

**Negative**
- У момент інциденту heavy user може на короткий час знову повлинути на сусідів.
- Треба окремий metric + alert (нова observability робота).

**Neutral**
- Logs: `rate_limit.redis_unavailable` з рівнем WARN.

## Links
- SPEC: [SPEC.md](../SPEC.md) §AC-03
- Related: [ADR-0007](0007-sliding-window-rate-limit.md)
