---
name: plan-tests
description: >
  Use when user wants to write a test plan per SDLC stage 15 (test-plan)
  protocol. Triggers on "test plan for {slug}", "test plan for {feature}",
  "what we test", "test strategy", "stage 15 for {slug}",
  "/sdlc-plan-tests {slug}". Output: docs/features/{slug}/test-plan.md with
  unit/integration/E2E breakdown, AC mapping (each AC → ≥1 test),
  test data strategy. Prerequisite: docs/features/{slug}/PRD.md (stage 03,
  for AC mapping) — hard refuse if missing.
---

# Skill: plan-tests (SDLC stage 15)

Test-plan generator: what we test and how — before writing tests. Breakdown unit/integration/E2E + contract tests + load/stress (for NFR). Each AC from PRD → ≥1 test. Test data strategy (factories / fixtures / testcontainers). Produces `docs/features/<slug>/test-plan.md`.

This is the **stage 15 runner**: plan is approved by QA + Backend before tests are written. Claude writes tests against this plan, not "however it seems".

## Owner

QA / Backend.

## When to use

- "test plan for <slug>", "test plan for <feature>", "test strategy for <slug>", "run stage 15".
- User has PRD (with AC) and is about to write tests / contract / load.
- `/sdlc-plan-tests <slug>` as explicit invocation.
- Skip if test-plan exists and is approved by QA + Backend lead.

## Inputs

- `<slug>` — same as for PRD.
- **Gate (hard refuse):** `docs/features/<slug>/PRD.md` must exist with Given/When/Then AC (for mapping). If not — STOP, suggest `sdlc:write-prd <slug>`.
- Sequence diagrams (for contract tests).

## Protocol

1. **Prereq check (hard).** `test -f docs/features/<slug>/PRD.md` → exit ≠ 0 = refuse + suggest `sdlc:write-prd <slug>`.
2. **Read prereqs.** PRD (AC in Given/When/Then), sequence diagrams (for contract tests), data-model (test data shape), API contract (for contract tests).
3. **Copy template.** Copy `./templates/test-plan.md` → `docs/features/<slug>/test-plan.md`.
4. **Test pyramid.** For the feature enumerate: (a) unit — pure logic (rating, validation), (b) integration — DB + repo + service, (c) E2E via HTTP API (1-2 per critical flow), (d) contract — between services, (e) load/stress — if there are NFR with numbers (throughput, p95).
5. **AC mapping.** Each AC from PRD → at least 1 test (can be unit + integration + E2E for the same AC). If an AC has no coverage — anti-pattern, PRD drives tests.
6. **Edge cases / error paths.** Separate tests for each error AC. For example: quota exceeded → 429; Redis down → 200 (fail-open).
7. **Test data strategy.** Factories (for unit), fixtures (integration / E2E), real DB via testcontainers. Mock DB — anti-pattern (mock passes, prod breaks).
8. **Coverage targets.** Not "100% coverage" but critical paths + happy + error paths. Can specify line coverage as guideline (≥80% domain), but the point is critical paths.
9. **E2E environment.** How it spins up (docker compose / kind / staging), how cleanup (truncate / drop). Without cleanup — flaky tests.
10. **Load / stress (NFR).** If PRD has NFR "p95 ≤ 5ms", "50k/s" — concrete load scenario (k6 / locust / vegeta) with command.
11. **Fill draft.** Fill test-plan; `<!-- TBD -->` for load scenarios without an approved tool.
12. **Self-check against DoD.** Each AC → ≥1 test, edge cases purposeful, test data strategy described, E2E env / cleanup written down.
13. **Propose commit.** `15: test-plan for <slug>` + next owner (Tech Lead → stage 16 review-checklist).

## Questions for discussion

- What do we test unit / integration / E2E?
- Contract tests (between services)?
- Load / stress (for NFR)?
- Test data: factories? fixtures? real DB via testcontainers?
- Coverage targets (line / branch — or list of critical paths)?

## Definition of Done

- Each AC → ≥1 test.
- Edge cases / error paths have dedicated tests.
- Test data strategy described.
- For E2E — test environment and cleanup approach.
- Plan approved by QA + Backend.

## Anti-patterns

- 100% coverage as the goal. Better — critical paths + happy + error paths.
- Tests after code — written "so they exist". TDD or test-first for new code.
- Mocking databases. Better testcontainers + real DB — mock pass != prod pass.
- No stress / load tests for NFR. "50k/s" stays theoretical.
- AC without coverage. PRD AC needs ≥1 test, otherwise PRD isn't verified.
- E2E without cleanup — flaky tests, each one blocks CI.
- Test plan as a wishlist "would be nice to add". A plan is a commitment.

## Template

→ [./templates/test-plan.md](./templates/test-plan.md)

## Example invocation

> **User:** "test plan for rate-limiting-per-user"
>
> **Skill behavior:**
> 1. `test -f` PRD → OK.
> 2. PRD AC: AC1 (within quota → 200), AC2 (over quota → 429 + Retry-After), AC3 (Redis down → fail-open, log).
> 3. Copies template → `docs/features/rate-limiting-per-user/test-plan.md`.
> 4. Pyramid: unit (token-bucket algorithm), integration (middleware + Redis testcontainer), E2E (full APIGW flow), contract (openapi → real responses), load (k6 at 60k/s sustain).
> 5. AC mapping: AC1 → unit `TestTokenBucket_WithinQuota` + E2E `test_quota_happy`; AC2 → unit + E2E `test_quota_exceeded_returns_429_with_retry_after`; AC3 → integration with Redis testcontainer killed.
> 6. Edge: tenant_id missing → 400; malformed Idempotency-Key → 400; Quota_config DELETE → cache invalidation.
> 7. Test data: factory for Tenant/QuotaConfig (Go faker), Redis testcontainer per test class.
> 8. Coverage: critical paths 100% (middleware/rate-limit/), domain 80%+.
> 9. E2E env: `docker compose up -d` (APIGW + Redis + Postgres + middleware), cleanup = `TRUNCATE quota_config`.
> 10. Load: k6 scenario 60k/s for 5 min, p95 < 5ms — runs via `make load-test`.
> 11. Self-check DoD → all AC covered, test data strategy OK, load OK.
> 12. Commit: `15: test-plan for rate-limiting-per-user`.
