---
status: Approved
owner: Anna
reviewers: [Kyrylo]
updated_at: "2026-05-13"
feature_size: S
stage: "01"
ticket: INC-841
---

# Idea brief — rate-limiting

**Author:** Anna (PM)
**Date:** 2026-05-13
**Rough size:** S

## Problem
За останній тиждень 3 B2B клієнти поскаржилися на `429 Too Many Requests` від нашого API. Розслідування показало: один heavy-user шле ~10k req/min, що вибиває глобальний rate limit і блокує сусідів. Поточний rate limit — per-IP, агрегує всіх.

## Users
B2B клієнти на shared API tier (~120 акаунтів). Особливо болить ентерпрайз-сегменту, у якого підписаний SLA по доступності.

## Why now
- Підписаний contract з Acme Corp обіцяє per-user SLA до кінця кварталу.
- Heavy users з beta-програми ламають shared limits — інциденти #INC-841, #INC-842, #INC-849.

## Out of scope
- Динамічні тарифи / billing (окремий roadmap).
- Per-endpoint квоти (тільки per-user / per-key для початку).
- Rate limit на WebSocket-зʼєднання.

## Related
- INC-841 — heavy-user blocked tenants in EU region
- Contract draft — Acme Corp SLA addendum
