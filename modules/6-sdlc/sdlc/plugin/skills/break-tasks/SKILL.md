---
name: break-tasks
description: >
  Use when user wants to break implementation into atomic tasks per SDLC
  stage 13 (task-breakdown) protocol. Triggers on "task breakdown for
  {slug}", "break down tasks for {feature}", "tasks for {slug}", "sprint plan
  for {feature}", "stage 13 for {slug}", "/sdlc-break-tasks {slug}". Output:
  docs/features/{slug}/tasks/_epic.md + tasks/tracker.md + tasks/<task>.md
  with atomic tasks ≤1 day each + dependency graph + DoD per task.
  Prerequisite: docs/features/{slug}/PRD.md + sad.md + ≥1 Accepted ADR — hard
  refuse if missing. Stories LINK to upstream artefacts (PRD AC §, SAD §6,
  data-model, openapi), they do not duplicate them.
---

# Skill: break-tasks (SDLC stage 13)

Task-breakdown generator: atomic tasks ≤1 day, each = a separate reviewable PR (≤500 LOC preferred). Dependency graph visible. DoD at the task level (tests / docs / migration). Produces `docs/features/<slug>/tasks/_epic.md` + `tasks/tracker.md` + one `tasks/<task-slug>.md` per task.

Story files LINK to upstream artefacts — `PRD.md §AC-N`, `sad.md §6 UC-N`, `data-model.md`, `api/openapi.yaml`, `adr/NNNN-*.md`. They do not duplicate them ("story лінкує, не дублює" — from Lecture 6.7).

This is the **stage 13 runner**: one task = one Claude session = one PR. "Build the feature" is not a task, break it down.

## Owner

Tech Lead.

## When to use

- "task breakdown for <slug>", "break down tasks for <feature>", "sprint plan for <feature>", "run stage 13".
- User has PRD + sad.md + Accepted ADRs and is about to create tickets in Jira / Linear / Issues.
- `/sdlc-break-tasks <slug>` as explicit invocation.
- Skip if task-breakdown exists and tickets are already created in the tracker.

## Inputs

- `<slug>` — same as for the feature.
- Upstream artefacts read DIRECTLY: PRD.md (AC, NFR), sad.md (§4 strategy, §5 module boundaries, §6 runtime, §9 ADR index), adr/* (Accepted decisions), (opt.) data-model.md, (opt.) api/openapi.yaml, (opt.) diagrams/seq-*.md, (opt.) migration-plan.md.
- **Gate (hard refuse):** `docs/features/<slug>/PRD.md` + `docs/features/<slug>/sad.md` + ≥1 Accepted ADR. If not — STOP, suggest the relevant upstream skill.

## Protocol

1. **Prereq check (hard).** `test -f docs/features/<slug>/PRD.md && test -f docs/features/<slug>/sad.md && ls docs/features/<slug>/adr/*.md` → exit ≠ 0 = refuse with the missing artefact.
2. **Read upstream artefacts DIRECTLY.** PRD AC + NFR (what to deliver), sad.md §5 (module boundaries — task scope) + §6 (runtime flows) + §9 (ADR index), each Accepted ADR (constraints), data-model.md (invariants if DB), openapi.yaml (contract). No intermediate index — each story will link back to the section it derives from.
3. **Scaffold output.** `mkdir -p docs/features/<slug>/tasks/` → create `tasks/_epic.md` (epic summary + links to PRD/SAD/ADRs), `tasks/tracker.md` (status table per task), and one `tasks/<task-slug>.md` per task (story body).
4. **Identify work-items by layer.** Typical layers: migration (DB), domain/entity, infra/repo, app/service, ports/handler, tests, docs. List 8-20 items depending on M+/S+.
5. **Atomic check.** Each task — ≤1 working day. If more — split. If PR > 500 LOC — suspect a task that is too wide.
6. **Dependencies graph.** For each task — `deps: [task_a, task_b]`. Identify parallel branches (e.g., migration and API can go in parallel if both land in domain test later).
7. **Per-task DoD.** Each task — testable: "tests pass", "migration applied on staging", "API responds 200 on example from openapi". Without DoD per task — subjective "when I decide myself".
8. **Estimate.** S/M/L or hours. If team uses sizing (Fibonacci) — adapt.
9. **Ownership.** For each task — named owner (placeholder `<TBD lead>` is OK for open). Without owner — task doesn't start.
10. **Tickets export (optional).** If MCP is available to Jira / Linear / GitHub Issues — propose creating tickets from `tasks/_epic.md` + `tasks/<task>.md`. Otherwise — copy-paste hints.
11. **Fill draft.** Fill breakdown; `<!-- TBD -->` for unknown estimates (reserve a spike).
12. **Self-check against DoD.** Each task ≤1 day, dependency graph visible, DoD per task, owners assigned.
13. **Propose commit.** `13: task-breakdown for <slug>` + next owner (Tech Lead → stage 14 claude-context).

## Questions for discussion

- Dependencies between tasks (graph)?
- What parallelizes?
- DoR / DoD per task?
- Who is the owner?
- Estimate (S/M/L or hours)?

## Definition of Done

- Tickets created, lined up in sprint / queue.
- Owners assigned.
- Each task ≤1 working day; if more — split.
- Each task = reviewable PR (≤500 LOC preferred).
- Dependency graph visible (sequence, or deps list in each ticket).
- DoD at the task level: tests / docs / migration.

## Anti-patterns

- Task "build the feature" — not a task. Break into ≥8 atomic ones.
- Tasks of 5 days = monster PR — impossible to review. Split.
- Without dependencies — start in parallel, blocked the next day because `task_x` is needed in `task_y`.
- Tasks without DoD per task — "when I decide myself it's ready".
- Tasks without owner — task doesn't start or everyone thinks the other will start.
- Sizing without reference (S/M/L). If team has no calibration — explain that S = 2h, M = half-day, L = day, otherwise split.
- Tasks that break Hard Rules from PRD §NFR / sad.md §11 — e.g. "change module/<other>" when the architecture forbids it.
- Story body duplicates PRD AC / SAD §6 / data-model verbatim — should LINK, not paste. ("story лінкує, не дублює" — Lecture 6.7.)

## Template

→ [sdlc/document-templates/task-breakdown.md](../../../document-templates/task-breakdown.md)

## Example invocation

> **User:** "task breakdown for rate-limiting-per-user"
>
> **Skill behavior:**
> 1. `test -f` PRD + sad.md + ADR-0001 → OK.
> 2. Reads PRD AC, sad.md §5 (module `middleware/rate-limit/*`, `internal/quota-config/*`), data-model (migration 042), ADR-0001.
> 3. `mkdir -p docs/features/rate-limiting-per-user/tasks/` → writes `_epic.md`, `tracker.md`, and 10 `<task-slug>.md` stories that LINK to PRD §AC-3 / sad.md §6 UC-1 / ADR-0001 instead of duplicating their content.
> 4. Tasks: (T1) migration 042 + rollback script; (T2) entity `RateLimitTier` + `QuotaConfig` domain; (T3) repo for quota-config; (T4) service `QuotaConfigService`; (T5) handler `POST /v1/quota-configs` + tests; (T6) handler `GET/PATCH/DELETE` + tests; (T7) middleware (Redis token-bucket); (T8) wiring in APIGW; (T9) metrics + event `rate_limit.exceeded.v1`; (T10) E2E test on happy + 429.
> 5. Each ≤1 day. T5/T6 split because together >500 LOC.
> 6. Deps: T2→T3→T4→T5→T6; T1 parallel with T2; T7→T8→T10; T4→T7; T9→T8.
> 7. DoD: T1 — migration applied + rollback tested on staging; T5 — handler tests pass + openapi example valid; T10 — E2E green.
> 8. Estimate: T1=S, T2=M, T7=L, ... total ~9 person-days.
> 9. Owners: T1-T4 — @alice; T5-T8 — @bob; T9-T10 — @charlie.
> 10. Self-check DoD → atomic ✅, deps ✅, DoD per task ✅.
> 11. Commit: `13: task-breakdown for rate-limiting-per-user`.
