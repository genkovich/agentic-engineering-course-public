---
status: Draft
owner: "<Tech Lead name>"
reviewers: []
updated_at: "<YYYY-MM-DD>"
feature_size: S
stage: "16"
ticket: "<ticket-id>"
---

# Review checklist — <feature>

<!-- Stage 16 → see SDLC/plugin/skills/prep-review/SKILL.md -->
<!-- ≤25 items. Relevant to the domain. -->

## Correctness
- [ ] ACs from SPEC are covered by tests.
- [ ] Edge cases / error paths have tests.
- [ ] No TODO / FIXME without owner+ticket.

## Security
- [ ] Input validation at boundary (HTTP / queue).
- [ ] No secrets in code / configs.
- [ ] SQL — parameterized queries (no string concat).
- [ ] Auth checked on all mutating endpoints.

## Performance
- [ ] No N+1 (especially on list endpoints).
- [ ] Indexes exist for new query patterns.
- [ ] No logs on hot path in tight loops.

## Observability
- [ ] Structured logs with `trace_id`.
- [ ] Metrics for new code points.
- [ ] Alerts / SLO updated (if relevant).

## Migrations
- [ ] Backward-compatible.
- [ ] Rollback tested on staging.
- [ ] No exclusive locks on large tables during business hours.

## API
- [ ] OpenAPI updated.
- [ ] Error codes in `module.error_name` format.
- [ ] Idempotency-Key for mutating + retriable.

## Docs
- [ ] CHANGELOG entry.
- [ ] README / runbook updated (if operations changed).
- [ ] ADR updated / new one created (if a decision changed).
