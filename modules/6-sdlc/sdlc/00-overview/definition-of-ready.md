# Definition of Ready

Before the first line of code is written (by a human or by Claude), the feature must pass this checklist.

- [ ] **SPEC merged**, AC in Given / When / Then format.
- [ ] **Architecture brief approved** (Lead + Senior).
- [ ] **C4 context + container** exist (for M+ — also component).
- [ ] **API contract** fixed: OpenAPI / GraphQL SDL / AsyncAPI. Mock server boots up.
- [ ] **Data-model + migration-plan** (if there is a DB), rollback-plan too.
- [ ] **ADRs for key trade-offs** recorded with status Accepted.
- [ ] **Implementation Pack** links all artefacts above and contains Hard Rules.
- [ ] **Task breakdown**: each task ≤1 day of work, with DoR/DoD/deps.
- [ ] **Claude execution context** self-contained: files, commands, hard rules, out-of-scope.
- [ ] **Review checklist** attached to the PR template.
- [ ] **Test plan** covers each AC with at least one test.
- [ ] **Security review** exists for M+, public, API, or data-heavy tasks.
- [ ] **Rollout plan** exists for feature flag, canary / staged rollout, or changes with rollback risk.

If even one item is unchecked — go back to the corresponding stage. No "let's start coding in parallel, we'll finish later" — that guarantees rework.

## DoR for XS/S tasks

It is acceptable to skip: arc42, deployment diagram, full C4 component, separate test-plan (can be inline in SPEC), security-review, and feature-rollout-plan if there is an explicit N/A in SPEC / architecture brief. Everything else — mandatory.
