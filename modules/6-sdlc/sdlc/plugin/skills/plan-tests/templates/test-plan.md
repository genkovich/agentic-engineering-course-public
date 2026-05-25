---
status: Draft
owner: "<QA owner>"
reviewers: ["<Tech Lead name>"]
updated_at: "<YYYY-MM-DD>"
feature_size: S
stage: "15"
ticket: "<ticket-id>"
---

# Test plan — <feature>

<!-- Stage 15 → see SDLC/plugin/skills/plan-tests/SKILL.md -->

## Levels

| Level | Scope | Tooling |
|---|---|---|
| Unit | Pure domain functions | <test framework> |
| Integration | Module ↔ DB / Redis / external (mocked at boundary) | testcontainers |
| Contract | OpenAPI / events | <spectral / pact> |
| E2E | Full HTTP flow | <Playwright / curl scripts> |
| Load | NFR validation | <k6 / locust> |

## AC coverage

| AC | Test(s) | Level |
|---|---|---|
| AC-01 | <test name> | integration |
| AC-02 | <test name> | E2E |

## Edge cases / error paths
- <case 1> → expected: <...>
- <case 2> → expected: <...>

## Test data
- Strategy: <factories / fixtures / generators>.
- Cleanup: <per-test / per-suite>.

## NFR validation
- p95 latency ≤ <Nms> → load test config: <...>
- Throughput ≥ <N rps> → <...>

## CI
- <which suites run on PR / nightly / release>
