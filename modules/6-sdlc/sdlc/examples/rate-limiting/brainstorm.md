---
status: Approved
owner: Kyrylo
reviewers: [Anna, Backend Lead]
updated_at: "2026-05-13"
feature_size: S
stage: "02"
ticket: INC-841
---

# Brainstorm — rate-limiting

**Driver:** Kyrylo (Tech Lead)
**Date:** 2026-05-13
**Participants:** Kyrylo, Backend Lead, Claude

## Context
Поточний rate limit — per-IP, in-memory у API. Треба per-user (по `user_id` з auth-токена), shared між replicas, з 429 + Retry-After. Очікуваний навантаження — 120 acc × до 100 req/min = ~12k req/min total.

## Options

| # | Option | Pros | Cons | Cost | Risk |
|---|--------|------|------|------|------|
| 1 | Token bucket у Redis | Простий, sliding-like behavior, дешевий | Не fair при burst, треба тюнити refill | S | low |
| 2 | Sliding window log у Redis | Точний, fair, легко пояснити SLA | Більше памʼяті (один ключ — список timestamps) | M | low |
| 3 | In-memory per-replica з gossip | Без Redis dependency | Потребує синхронізацію, складно тестувати, нестійко при scale-out | L | high |

## Risks
- **Redis як єдина точка відмови** — probability: low, impact: high. Mitigation: Redis cluster + fallback (fail-open) при недоступності + alert.
- **Хибне списання при гонці** — probability: med, impact: low. Mitigation: atomic Lua-script.
- **Memory blowup у Sliding window** — probability: low, impact: med. Mitigation: TTL = window, max log size cap.

## Unknowns
- Чи треба per-endpoint в майбутньому? → spike-питання продукту (закрив: «не треба у фазі 1»).
- Точна цифра RPS на peak? → перевірити в Grafana за останні 30 днів (peak ~14k req/min total).

## Recommendation
**Option 2: Sliding window log у Redis.** Чому: AC вимагає точність «100 req/min per user», а token bucket дає approximation. Memory cost при 120 acc × 100 events = 12k records у Redis — дешево.

## Open questions
- [x] Чи fail-open чи fail-closed при недоступності Redis? → Tech Lead: **fail-open + alert**. Закрито 2026-05-13.
- [x] Як комунікувати клієнтам про 429? → Retry-After header + docs. Закрито 2026-05-13.
