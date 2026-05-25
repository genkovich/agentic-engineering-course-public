---
status: Approved
owner: Backend Lead
reviewers: [Kyrylo]
updated_at: "2026-05-14"
feature_size: S
stage: "08"
ticket: INC-841
---

# Data model — Rate limiting

Зберігаємо стан у Redis. SQL-міграцій немає.

## Redis schema

| Key | Type | Value | TTL | Purpose |
|---|---|---|---|---|
| `rl:<user_id>` | Sorted Set | members = `<request_uuid>`, score = `<epoch_ms>` | 120s (≥ window) | Sliding window log per user |

## Algorithm (atomic Lua)

1. `ZREMRANGEBYSCORE rl:<user_id> -inf (now - window_ms)` — drop старі записи.
2. `ZCARD rl:<user_id>` — поточна кількість.
3. Якщо `count >= limit`:
   - Дістати найстаріший: `ZRANGE rl:<user_id> 0 0 WITHSCORES` → `retry_after = (oldest + window) - now`.
   - Повернути `{ allowed: 0, retry_after }`.
4. Інакше:
   - `ZADD rl:<user_id> <now> <uuid>`.
   - `EXPIRE rl:<user_id> 120`.
   - Повернути `{ allowed: 1, count: count+1 }`.

## Access patterns

| Pattern | Operation | Frequency |
|---|---|---|
| Decide allow/deny per request | EVAL Lua | ~14k req/min total |
| Cleanup (lazy) | ZREMRANGEBYSCORE при кожному decision | inline |
| TTL eviction | Redis auto | inline |

## Sizing
- Active users (peak): ~120.
- Max entries per user: 100 (≥ limit).
- Total memory: ~120 × 100 × ~80 bytes ≈ 1MB. Mizernio.

<!-- Why: sliding window log дає точність, а не approximation. Memory cost — низький. -->
