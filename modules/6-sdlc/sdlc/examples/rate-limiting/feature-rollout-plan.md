---
status: shipped
owner: Release manager
reviewers: [Kyrylo, SRE]
updated_at: "2026-05-20"
feature_size: S
stage: "rollout"
ticket: INC-841
---

# Feature rollout plan — Rate limiting

## Control
- Feature flag: `api.rate_limit_per_user`.
- Default state: off before rollout, on after post-release verification.
- Kill switch: disable flag in central config and reload API config.
- Rollback owner: Release manager.

## Rollout steps

| Step | Audience | Percent / scope | Duration | Entry criteria | Exit criteria |
|---|---|---|---|---|---|
| 1 | Internal | Staff API keys | 4h | CI green | no Redis errors |
| 2 | Canary | 5% B2B tenants | 24h | internal stable | 429 complaints do not increase |
| 3 | Staged | 25% -> 50% -> 100% | 48h | canary green | p95 overhead <= 5ms |

## Monitoring window
- Start: 2026-05-20 09:00 Europe/Budapest.
- Duration: 72h.
- Dashboard: Grafana API / RateLimit.
- Alerts: `rate_limit_redis_errors_total`, API p95, 429 ratio.

## Thresholds
- Error rate: rollback if API 5xx > 1% for 10m.
- Latency: rollback if middleware p95 > 5ms for 15m.
- Business metric: rollback if valid tenant traffic gets 429 above expected quota behavior.

## Rollback
1. Disable `api.rate_limit_per_user`.
2. Roll API deployment back if headers or middleware ordering still affect responses.
3. Verify p95 and 429 ratio return to baseline.
4. Notify support if customer-visible.

## Post-release verification
- [x] AC smoke tests passed in production.
- [x] Dashboards stable through monitoring window.
- [x] Support / on-call notified.
- [x] Follow-up created for per-endpoint quotas.
