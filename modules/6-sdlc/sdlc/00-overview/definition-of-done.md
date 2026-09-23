# Definition of Done

A feature is considered complete when all items are closed. Otherwise — it's in-progress.

- [ ] **All tasks closed**, AC verified (PM/QA confirmed). `tasks/tracker.md` shows all tasks done; `tasks/tasks.json` AC rows satisfied.
- [ ] **Tests per test-plan, CI green** (unit + integration + contract + E2E where relevant).
- [ ] **Migration promoted and executed on staging**, rollback scenario tested. Staged `docs/features/<slug>/migrations/` promoted to live migrations tree by `implement-tasks`.
- [ ] **OpenAPI updated**, contract tests pass (`contracts/openapi.yaml` + `api-sync-report.md`).
- [ ] **ADR updated** if the decision changed during implementation.
- [ ] **review-feature PASS** — `_review/review-<date>.md` verdict is PASS (AC end-to-end trace + quality stage both clear). This is the hard gate before shipping.
- [ ] **CHANGELOG entry** added and **PR body** created by `ship-feature` (Keep-a-Changelog: Added/Changed/Fixed/Removed + Breaking; includes AC/ADR links + SDLC-Task commit history).
- [ ] **Roadmap updated** — feature row moved to Shipped in `docs/roadmap.md` by `ship-feature`.
- [ ] **Observability**: logs/metrics/alerts enabled for new code points.
- [ ] **Documentation**: README/runbook updated if operations changed.

## What is NOT DoD

- Feature flag enabled in prod (this is a separate rollout step).
- 100% test coverage (aim for coverage of **critical paths**, not the number).
- Slack announcement / marketing — out of scope for SDLC.
- KB/Obsidian vault sync — useful but happens after merge, not a gate on the PR.
