---
status: Approved
owner: Anna
reviewers: [Kyrylo]
updated_at: "2026-05-14"
feature_size: S
stage: "03"
ticket: INC-841
aliases: [PRD]
---

# SPEC — Rate limiting per user

**Status:** Approved
**PM:** Anna
**Tech Lead:** Kyrylo
**Last updated:** 2026-05-14

## 1. Context
API має глобальний per-IP rate limit. Heavy users ламають shared limit і блокують сусідів. Контракт з Acme Corp вимагає per-user SLA.

## 2. Goals
- Кожен користувач отримує власну квоту RPM.
- Heavy user не впливає на сусідів.
- Чесний механізм (sliding window, не token bucket approximation).

## 3. Non-goals
- Per-endpoint квоти (фаза 2).
- Динамічні тарифи / billing (інший roadmap).
- Rate limit для WebSocket.

## 4. User stories

### US-01: Окрема квота на користувача
**As a** B2B клієнт
**I want** мати власну квоту 100 req/min
**So that** інші користувачі не блокували мій трафік

### US-02: Інформативна відмова
**As a** клієнтська інтеграція
**I want** при перевищенні отримати `429` з `Retry-After`
**So that** я знав, коли можна спробувати знову

## 5. Acceptance criteria

### AC-01 (US-01)
**Given** користувач `U1` відправив 100 успішних запитів за останні 60 секунд
**When** він шле 101-й запит
**Then** отримує `HTTP 429` з заголовком `Retry-After: seconds` і body `{"code":"rate_limit.exceeded","message":"Too many requests. Try again later."}`.

### AC-02 (US-01)
**Given** користувач `U1` отримав `429`
**When** користувач `U2` шле запит у ту ж хвилину
**Then** `U2` отримує `200` (його квота не зачеплена).

### AC-03 (Redis fail-open)
**Given** Redis недоступний
**When** користувач шле запит
**Then** запит проходить (fail-open) + лог `rate_limit.redis_unavailable` + alert.

## 6. Non-functional requirements

| Aspect | Target | Measurement |
|--------|--------|-------------|
| Latency p95 (middleware overhead) | ≤ 5ms | API metrics |
| Throughput | 14k req/min total | load test |
| Availability | rate limit не зменшує SLA API | синтетичний моніторинг |
| Security | не можна обійти підміною токена | auth перевіряється до rate limit |

## 6.1 Security / privacy
- Data classification: internal operational metadata; no new PII fields.
- Personal data touched: `user_id` from an already-authenticated token; not logged in raw form.
- AuthZ/AuthN impact: Auth middleware must run before rate limiting so clients cannot choose another user key.
- Abuse cases: high-RPS tenant, replayed tokens, Redis timeout flood.
- Security review: N/A for S-size internal middleware change; checklist security section covers boundary controls.

## 7. Metrics / KPIs
- `rate_limit_decisions_total{decision=allow|deny}` — кількість.
- `rate_limit_redis_errors_total` — fail-open інциденти.
- Скарги клієнтів на 429 від сусідів — baseline 3/тиждень, target: 0.

## 8. Open questions
- [x] Fail-open чи fail-closed → fail-open + alert (закрито в brainstorm).
- [x] Чи різні tier-ліміти зараз → ні, один tier 100 RPM (фаза 1).
