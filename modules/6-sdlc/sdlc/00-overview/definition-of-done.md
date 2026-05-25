# Definition of Done

A feature is considered complete when all items are closed. Otherwise — it's in-progress.

- [ ] **All tasks closed**, AC verified (PM/QA confirmed).
- [ ] **Tests per test-plan, CI green** (unit + integration + contract + E2E where relevant).
- [ ] **Migration executed on staging**, rollback scenario tested.
- [ ] **OpenAPI updated**, contract tests pass.
- [ ] **ADR updated** if the decision changed during implementation.
- [ ] **CHANGELOG entry** added (Keep-a-Changelog: Added/Changed/Fixed/Removed + Breaking).
- [ ] **KB note** written and merged into the Obsidian vault, backlinks to ADR + SPEC.
- [ ] **Observability**: logs/metrics/alerts enabled for new code points.
- [ ] **Documentation**: README/runbook updated if operations changed.

## What is NOT DoD

- Feature flag enabled in prod (this is a separate rollout step).
- 100% test coverage (aim for coverage of **critical paths**, not the number).
- Slack announcement / marketing — out of scope for SDLC.
