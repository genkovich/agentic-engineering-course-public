---
status: shipped
owner: Release manager
reviewers: [Kyrylo]
updated_at: "2026-05-20"
feature_size: S
stage: "17"
ticket: INC-841
---

# Changelog

## [0.2.0] - 2026-05-20

### Added
- Per-user API rate limiting with Redis-backed sliding window log.
- `429` response contract with `Retry-After` and `X-RateLimit-*` headers.
- Fail-open Redis behavior with metrics and alerting.
